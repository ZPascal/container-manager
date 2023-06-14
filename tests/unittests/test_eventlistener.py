import io
from pathlib import Path
import os
import shutil
from unittest import TestCase
from unittest.mock import MagicMock, patch, mock_open

from files.image.supervisord import eventlistener


class EventListenerTestCase(TestCase):
    @staticmethod
    def assertIsFile(path):
        if not Path(path).resolve().is_file():
            raise AssertionError(f"File does not exist: {str(path)}")

    @patch("builtins.open", new_callable=mock_open)
    def test_write_file(self, open_mock):
        self.assertEqual(None, eventlistener._write_file(MagicMock(), MagicMock()))

    @patch("builtins.open", new_callable=mock_open)
    def test_write_file_no_rights_to_create_the_file(self, mock_open):
        mock_open.side_effect = Exception
        with self.assertRaises(Exception):
            eventlistener._write_file(MagicMock(), MagicMock())

    def test_write_pid_file(self):
        tmp_dir_folder: str = f"{os.getcwd()}{os.sep}tmp-dir"
        os.mkdir(tmp_dir_folder)
        eventlistener._write_pid_file(tmp_dir_folder, "test", 1)

        path: Path = Path(f"{tmp_dir_folder}{os.sep}supervisor.test.pid")
        self.assertIsFile(path)

        with open(path, "r") as file:
            output: str = file.readline()

        self.assertEqual(1, int(output))
        shutil.rmtree(tmp_dir_folder)

    def test_write_state_file(self):
        tmp_dir_folder: str = f"{os.getcwd()}{os.sep}tmp-dir"
        os.mkdir(tmp_dir_folder)
        eventlistener._write_state_file(tmp_dir_folder, "test", "test")

        path: Path = Path(f"{tmp_dir_folder}{os.sep}supervisor.test.state")
        self.assertIsFile(path)

        with open(path, "r") as file:
            output: str = file.readline()

        self.assertEqual("test", output)
        shutil.rmtree(tmp_dir_folder)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_write_stdout(self, stdout_mock):
        eventlistener._write_stdout("test")

        self.assertEqual("test", stdout_mock.getvalue())

    @patch("sys.stderr", new_callable=io.StringIO)
    def test_write_stderr(self, stdout_mock):
        eventlistener._write_stderr("test")

        self.assertEqual("test", stdout_mock.getvalue())
