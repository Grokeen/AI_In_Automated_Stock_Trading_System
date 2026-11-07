#!/usr/bin/env python3
# Created 2026-11-08 03:22 KST: deploy bounded logging and NAS monitoring with verified backups.
"""Use --check to inspect the plan or --apply to deploy on the NAS itself."""

import argparse
from datetime import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile

SOURCE = Path(__file__).resolve().parents[1]
BACKUPS = Path('/var/backups/nas-trading-maintenance')
MANAGED_HEADER = b'# Created 2026-11-08 03:22 KST:'
FILES = {
    SOURCE / 'nas/healthcheck.py': Path('/opt/nas-trading-tools/healthcheck.py'),
    SOURCE / 'deploy/60-nas-trading.conf': Path('/etc/systemd/journald.conf.d/60-nas-trading.conf'),
}
for name in ['nas-healthcheck.service', 'nas-healthcheck.timer',
             'nas-trading.slice', 'nas-trader.service']:
    FILES[SOURCE / 'deploy' / name] = Path('/etc/systemd/system') / name


def run(argv):
    result = subprocess.run(argv, capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise RuntimeError('{} failed: {}'.format(argv[0], result.stderr.strip()[-1500:]))
    return result.stdout.strip()


def digest(stream):
    checksum = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        checksum.update(block)
    return checksum.hexdigest()


def atomic_write(path, content, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix='.nas-install-', dir=str(path.parent))
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def backup_journals(directory):
    """Verify every archived journal before a retention setting can remove it."""
    journal = Path('/var/log/journal')
    if not journal.is_dir():
        return None
    required = sum(p.stat().st_size for p in journal.rglob('*') if p.is_file())
    if shutil.disk_usage(directory).free < required + 512 * 1024 ** 2:
        raise RuntimeError('Insufficient backup space; no retention change applied.')
    run(['journalctl', '--sync'])
    run(['journalctl', '--rotate'])
    paths = sorted(p for p in journal.rglob('*') if p.is_file() and not p.is_symlink()
                   and ('@' in p.name or p.name.endswith('.journal~')))
    checksums = {}
    archive = directory / 'archived-journals.tar.gz'
    print('Backing up {} archived journal files.'.format(len(paths)), flush=True)
    with tarfile.open(archive, 'w:gz', compresslevel=1) as tar:
        for path in paths:
            relative = str(path.relative_to('/var/log'))
            with path.open('rb') as stream:
                checksums[relative] = digest(stream)
            tar.add(path, arcname=relative, recursive=False)
    os.chmod(archive, 0o600)
    verified = {}
    with tarfile.open(archive, 'r|gz') as tar:
        for member in tar:
            stream = tar.extractfile(member)
            if stream is None:
                raise RuntimeError('Unexpected backup archive entry.')
            with stream:
                verified[member.name] = digest(stream)
    if verified != checksums:
        raise RuntimeError('Journal backup verification failed; no retention change applied.')
    with archive.open('rb') as stream:
        archive_checksum = digest(stream)
    print('Journal archive verification passed.', flush=True)
    return {'archive': str(archive), 'sha256': archive_checksum,
            'files': checksums, 'bytes': archive.stat().st_size}


def sync_folder2ram_logs():
    config = Path('/etc/folder2ram/folder2ram.conf')
    if not config.exists() or not shutil.which('folder2ram'):
        return
    entries = [line.split() for line in config.read_text().splitlines()
               if line.strip() and not line.lstrip().startswith('#')]
    for index, entry in enumerate(entries, 1):
        if len(entry) >= 2 and entry[0] == 'tmpfs' and entry[1] == '/var/log':
            output = run(['folder2ram', '-sync', str(index)])
            if 'sync of /var/log successful!' not in output:
                raise RuntimeError('folder2ram could not persist the reduced logs.')
            return


def vacuum_journals():
    # Updated 2026-11-08 03:27 KST: daemon startup retention can race journalctl cleanup.
    argv = ['journalctl', '--vacuum-size=128M', '--vacuum-time=14d']
    run(['journalctl', '--sync'])
    try:
        run(argv)
    except RuntimeError:
        # Retry once after a daemon synchronization barrier; persistent errors still abort.
        run(['journalctl', '--sync'])
        run(argv)


def restore_files(saved):
    for path, previous in saved.items():
        if previous is None:
            path.unlink(missing_ok=True)
        else:
            atomic_write(path, previous[0], previous[1])
    run(['systemctl', 'daemon-reload'])
    run(['systemctl', 'restart', 'systemd-journald'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--check', action='store_true')
    action.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    changes = {}
    for source, target in FILES.items():
        wanted = source.read_bytes()
        if target.is_symlink():
            raise RuntimeError('Refusing a symlink destination: ' + str(target))
        existing = target.read_bytes() if target.exists() else None
        if existing is not None and existing != wanted and MANAGED_HEADER not in existing[:250]:
            raise RuntimeError('Refusing to overwrite an unmanaged file: ' + str(target))
        if existing != wanted:
            changes[target] = wanted
    print(json.dumps({'planned_changes': [str(path) for path in changes],
                      'backup_root': str(BACKUPS), 'reboot_required': False,
                      'starts_trading': False}, indent=2), flush=True)
    if args.check:
        return 0
    if os.geteuid() != 0:
        raise RuntimeError('Run --apply through sudo on the NAS.')
    model = Path('/proc/device-tree/model').read_text().rstrip('\x00')
    if not model.startswith('Raspberry Pi 4'):
        raise RuntimeError('This deployment is scoped to the inspected Raspberry Pi 4.')
    with open('/run/lock/nas-trading-maintenance.lock', 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if not changes:
            print('Already installed; no files changed and no additional journal archive created.')
            return 0
        # Check again under the lock so another installer cannot race the initial plan.
        for target in changes:
            if target.exists() and MANAGED_HEADER not in target.read_bytes()[:250]:
                raise RuntimeError('Destination changed during deployment: ' + str(target))
        stamp = datetime.now().astimezone().strftime('%Y%m%dT%H%M%S%z')
        directory = BACKUPS / stamp
        directory.mkdir(parents=True, mode=0o700)
        os.chmod(BACKUPS, 0o700)
        saved = {target: (target.read_bytes(), target.stat().st_mode & 0o777)
                 if target.exists() else None for target in changes}
        manifest = {'created_at': datetime.now().astimezone().isoformat(),
                    'source': str(SOURCE), 'files': {}, 'completed': False}
        for target, previous in saved.items():
            backup = directory / 'files' / str(target).lstrip('/')
            if previous is not None:
                atomic_write(backup, previous[0], previous[1])
            manifest['files'][str(target)] = str(backup) if previous else None
        manifest['journal_backup'] = backup_journals(directory)
        manifest_path = directory / 'manifest.json'
        atomic_write(manifest_path, json.dumps(manifest, indent=2).encode(), 0o600)
        timer_was_active = subprocess.run(['systemctl', 'is-active', '--quiet',
                                           'nas-healthcheck.timer'], capture_output=True).returncode == 0
        timer_was_enabled = subprocess.run(['systemctl', 'is-enabled', '--quiet',
                                            'nas-healthcheck.timer'], capture_output=True).returncode == 0
        try:
            for target, wanted in changes.items():
                atomic_write(target, wanted)
            run(['systemd-analyze', 'verify'] + [str(path) for path in FILES.values()
                                               if path.suffix in ['.service', '.timer', '.slice']])
            run(['systemctl', 'daemon-reload'])
            run(['systemctl', 'restart', 'systemd-journald'])
            vacuum_journals()
            sync_folder2ram_logs()
            run(['systemctl', 'enable', '--now', 'nas-healthcheck.timer'])
            run(['systemctl', 'start', 'nas-healthcheck.service'])
            # Do not enable or start nas-trader.service: no broker application is configured.
            for target, wanted in FILES.items():
                if wanted.read_bytes() != target.read_bytes():
                    raise RuntimeError('Source changed during deployment; installed hash differs.')
            manifest['completed'] = True
            atomic_write(manifest_path, json.dumps(manifest, indent=2).encode(), 0o600)
        except Exception:
            if not timer_was_active:
                subprocess.run(['systemctl', 'stop', 'nas-healthcheck.timer'])
            if not timer_was_enabled:
                subprocess.run(['systemctl', 'disable', 'nas-healthcheck.timer'])
            restore_files(saved)
            raise
        print(json.dumps({'deployed': True, 'manifest': str(manifest_path),
                          'journal_usage': run(['journalctl', '--disk-usage']),
                          'health_snapshot': '/var/lib/nas-healthcheck/status.json'}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
