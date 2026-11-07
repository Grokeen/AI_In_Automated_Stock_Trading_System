#!/usr/bin/env python3
# Created 2026-11-08 03:22 KST: read-only Raspberry Pi NAS health collection.
"""Collect a small health snapshot without reading credentials or file contents."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def command(argv):
    """Return bounded command output; an unavailable probe stays visible."""
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=10)
        return {"ok": result.returncode == 0, "output": result.stdout.strip(),
                "error": result.stderr.strip()[:500]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "output": "", "error": str(exc)}


def read_meminfo(path=Path('/proc/meminfo')):
    values = {}
    for line in path.read_text().splitlines():
        key, value = line.split(':', 1)
        values[key] = int(value.strip().split()[0]) * 1024
    return values


def assess(snapshot):
    """Keep workload limits and actual NAS faults distinct in the report."""
    issues = []

    def add(level, code, message):
        issues.append({"level": level, "code": code, "message": message})

    available = snapshot['memory']['available_mib']
    if available < 256:
        add('critical', 'memory', 'Available memory is below 256 MiB.')
    elif available < 512:
        add('warning', 'memory', 'Available memory is below 512 MiB.')
    for disk in snapshot['disks']:
        if disk['used_percent'] >= 98:
            add('critical', 'disk', 'Storage at {} is {:.1f}% full.'.format(
                disk['mount'], disk['used_percent']))
        elif disk['used_percent'] >= 90:
            add('warning', 'disk', 'Storage at {} is {:.1f}% full.'.format(
                disk['mount'], disk['used_percent']))
    temp = snapshot.get('temperature_c')
    if temp is not None and temp >= 80:
        add('critical', 'temperature', 'CPU temperature is at least 80 C.')
    elif temp is not None and temp >= 75:
        add('warning', 'temperature', 'CPU temperature is at least 75 C.')
    for name, active in snapshot.get('services', {}).items():
        if not active:
            add('critical', 'service', '{} is not active.'.format(name))
    if not snapshot.get('clock_synchronized', False):
        add('warning', 'clock', 'NTP synchronization could not be confirmed.')
    for probe in snapshot.get('probe_errors', []):
        add('warning', 'probe', '{} could not be collected.'.format(probe))
    levels = {issue['level'] for issue in issues}
    status = 'critical' if 'critical' in levels else 'warning' if levels else 'ok'
    return status, issues


def collect():
    mem = read_meminfo()
    mounts = command(['findmnt', '--json', '--list', '--real',
                      '--output', 'TARGET,SOURCE,FSTYPE'])
    disks = []
    errors = []
    if mounts['ok']:
        for entry in json.loads(mounts['output']).get('filesystems', []):
            target = entry['target']
            if target != '/' and not target.startswith('/srv/dev-disk-by-'):
                continue
            try:
                usage = shutil.disk_usage(target)
                # Available blocks respect filesystem reserved space, unlike a simple used/total ratio.
                used_percent = 100 * usage.used / (usage.used + usage.free)
                disks.append({'mount': target, 'filesystem': entry['fstype'],
                              'used_percent': round(used_percent, 2),
                              'available_gib': round(usage.free / 1024 ** 3, 2)})
            except OSError:
                errors.append('disk:' + target)
    else:
        errors.append('mounts')
    try:
        temperature = int(Path('/sys/class/thermal/thermal_zone0/temp').read_text()) / 1000
    except (OSError, ValueError):
        temperature = None
        errors.append('temperature')
    clock = command(['timedatectl', 'show', '-p', 'NTPSynchronized', '--value'])
    controllers = Path('/sys/fs/cgroup/cgroup.controllers')
    snapshot = {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'memory': {'total_mib': round(mem['MemTotal'] / 1024 ** 2),
                   'available_mib': round(mem['MemAvailable'] / 1024 ** 2)},
        'disks': disks,
        'temperature_c': temperature,
        'load_average': list(os.getloadavg()),
        'services': {name: command(['systemctl', 'is-active', '--quiet', name])['ok']
                     for name in ['smbd', 'openmediavault-engined', 'nginx', 'docker']},
        'clock_synchronized': clock['ok'] and clock['output'] == 'yes',
        'capabilities': {
            'userland_architecture': command(['dpkg', '--print-architecture'])['output'],
            'kernel_architecture': os.uname().machine,
            'memory_cgroup': controllers.exists() and 'memory' in controllers.read_text().split(),
        },
        'probe_errors': errors,
    }
    snapshot['status'], snapshot['issues'] = assess(snapshot)
    return snapshot


def write_snapshot(path, data):
    """An interrupted write must not replace the previous complete snapshot."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_path = tempfile.mkstemp(prefix='.status-', dir=str(path.parent))
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    snapshot = collect()
    if args.output:
        write_snapshot(args.output, snapshot)
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    # A recorded critical disk state is distinct from a failed monitoring job.
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
