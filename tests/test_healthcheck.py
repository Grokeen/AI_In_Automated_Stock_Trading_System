# Created 2026-11-08 03:22 KST: verify actionable storage alerts and reliable status output.
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from nas.healthcheck import assess, read_meminfo, write_snapshot


class HealthcheckTests(unittest.TestCase):
    def setUp(self):
        self.healthy = {'memory': {'available_mib': 2048},
                        'disks': [{'mount': '/', 'used_percent': 11}],
                        'temperature_c': 63,
                        'services': {'smbd': True},
                        'clock_synchronized': True}

    def test_actual_nas_full_disks_are_not_hidden_by_free_root_disk(self):
        sample = copy.deepcopy(self.healthy)
        sample['disks'] += [{'mount': '/srv/dev-disk-by-full', 'used_percent': 99.9},
                            {'mount': '/srv/dev-disk-by-nearly-full', 'used_percent': 96.2}]
        status, issues = assess(sample)
        self.assertEqual(status, 'critical')
        self.assertEqual([item['level'] for item in issues], ['critical', 'warning'])
        self.assertIn('/srv/dev-disk-by-full', issues[0]['message'])

    def test_low_memory_and_service_outage_remain_separate(self):
        sample = copy.deepcopy(self.healthy)
        sample['memory']['available_mib'] = 128
        sample['services']['smbd'] = False
        status, issues = assess(sample)
        self.assertEqual(status, 'critical')
        self.assertEqual({issue['code'] for issue in issues}, {'memory', 'service'})

    def test_unavailable_probe_is_not_reported_as_healthy(self):
        sample = dict(self.healthy, probe_errors=['mounts'])
        self.assertEqual(assess(sample)[0], 'warning')

    def test_healthy_machine_has_no_incident(self):
        self.assertEqual(assess(self.healthy), ('ok', []))

    def test_meminfo_units(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'meminfo'
            path.write_text('MemTotal: 3885396 kB\nMemAvailable: 2700000 kB\n')
            self.assertEqual(read_meminfo(path)['MemAvailable'], 2700000 * 1024)

    def test_snapshot_replaces_old_complete_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'status.json'
            path.write_text('{"old":true}')
            write_snapshot(path, {'status': 'critical', 'issues': ['disk']})
            self.assertEqual(json.loads(path.read_text())['issues'], ['disk'])
            self.assertEqual([p.name for p in path.parent.iterdir()], ['status.json'])

    def test_failed_replace_preserves_last_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'status.json'
            path.write_text('{"old":true}')
            with patch('nas.healthcheck.os.replace', side_effect=OSError('simulated disk error')):
                with self.assertRaises(OSError):
                    write_snapshot(path, {'new': True})
            self.assertEqual(json.loads(path.read_text()), {'old': True})
            self.assertEqual(len(list(path.parent.iterdir())), 1)


if __name__ == '__main__':
    unittest.main()
