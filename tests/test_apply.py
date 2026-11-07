# Created 2026-11-08 03:27 KST: transient cleanup errors must not hide persistent failures.
import sys
import unittest
from unittest.mock import patch


@unittest.skipUnless(sys.platform.startswith('linux'), 'Linux deployment helper uses fcntl')
class DeploymentTests(unittest.TestCase):
    def test_cleanup_recovers_from_one_transient_error(self):
        from nas.apply import vacuum_journals
        with patch('nas.apply.run', side_effect=['', RuntimeError('journal changed'), '', '']) as run:
            vacuum_journals()
        self.assertEqual(run.call_count, 4)

    def test_persistent_cleanup_error_aborts_deployment(self):
        from nas.apply import vacuum_journals
        with patch('nas.apply.run', side_effect=['', RuntimeError('I/O error'), '',
                                               RuntimeError('I/O error')]):
            with self.assertRaisesRegex(RuntimeError, 'I/O error'):
                vacuum_journals()


if __name__ == '__main__':
    unittest.main()
