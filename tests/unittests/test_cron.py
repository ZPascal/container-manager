import os
import sys
from unittest import TestCase, main
from unittest.mock import MagicMock, patch, call, mock_open

from utils import Utils


def _extract_crontab_path() -> str:
    pwd: str = Utils._get_path_name()
    base_dir: str = os.path.dirname(os.path.dirname(pwd))
    cron_dir: str = f"{base_dir}{os.sep}files{os.sep}image{os.sep}cron"
    return cron_dir


sys.path.insert(0, _extract_crontab_path())

from files.image.cron import cron  # noqa: F401


class CronTestCase(TestCase):

    def test_parse_crontab(self):
        self.assertEqual(4, len(cron._parse_crontab(f"{Utils._get_path_name()}{os.sep}resources{os.sep}crontab")))

    def test_parse_crontab_no_valid_file(self):
        with self.assertRaises(SystemExit):
            cron._parse_crontab(f"{Utils._get_path_name()}{os.sep}resources{os.sep}crontab1")

    def test_parse_crontab_crontab_no_valid_lines(self):
        with self.assertRaises(SystemExit):
            cron._parse_crontab(f"{Utils._get_path_name()}{os.sep}resources{os.sep}crontab_error")

    def test_get_next_executions_empty_list(self):
        with self.assertRaises(ValueError):
            cron._get_next_executions([])

    def test_get_next_executions_valid_list(self):
        self.assertEqual((2, ['/image/config/env; /image/backup/backup.py 2>&1 >/storage/logs/backup.log']),
                         cron._get_next_executions(
                             [[MagicMock(),
                               '/image/config/env; /image/backup/backup.py 2>&1 >/storage/logs/backup.log']]
                         ))

    def test_loop_empty_list(self):
        with self.assertRaises(ValueError):
            cron._loop([])

    @patch("files.image.cron.cron._execute_command", MagicMock())
    @patch("files.image.cron.cron._get_next_executions")
    def test_loop_valid_list_and_test_mode(self, get_next_executions_mock):
        get_next_executions_mock.return_value = 1, [
            '/image/config/env; /image/backup/backup.py 2>&1 >/storage/logs/backup.log']
        cron._loop([[MagicMock(), '/image/config/env; /image/backup/backup.py 2>&1 >/storage/logs/backup.log']], True)

    @patch("subprocess.run")
    def test_execute_command_valid_command(self, subprocess_run_mock):
        subprocess_run_mock.return_value.stdout = "test"
        subprocess_run_mock.return_value.stderr = ""

        with self.assertLogs("exec", level="INFO") as cm:
            cron._execute_command("ls -la")
        self.assertEqual(["INFO:exec:Executing command ls -la", "INFO:exec:Standard output: test",
                          "INFO:exec:Standard error: "], cm.output)

    @patch("subprocess.run")
    def test_execute_command_non_valid_command(self, subprocess_run_mock):
        subprocess_run_mock.return_value.stdout = "test"
        subprocess_run_mock.return_value.stderr = "test"

        with self.assertLogs("exec", level="INFO") as cm:
            cron._execute_command("test")
        self.assertEqual(["INFO:exec:Executing command test", "INFO:exec:Standard output: test",
                          "INFO:exec:Standard error: test"], cm.output)

    def test_signal_handler(self):
        with self.assertRaises(SystemExit):
            cron._signal_handler()


if __name__ == "__main__":
    main()
