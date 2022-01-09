import os
import tarfile

from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from utils import Utils

os.environ[
    "IMAGE_BASE_DIR"
] = f"{os.path.dirname(os.path.dirname(Utils._get_path_name()))}/files/image"

from files.image.restore import restore  # noqa: E402


class RestoreTestCase(TestCase):
    def test_restore_data_no_backup_file(self):
        with self.assertRaises(SystemExit):
            restore.restore_data("")

    @patch("subprocess.Popen.communicate")
    def test_restore_data_backup_is_running(self, subprocess_run_mock):
        subprocess_run_mock.return_value = ("test", None)
        with self.assertRaises(SystemExit):
            restore.restore_data("test")

    def test_restore_data_backup_is_not_running_no_restore_scripts_dir(self):
        with self.assertRaises(SystemExit):
            restore.restore_data("test")

    def test_restore_data_backup_is_not_running_no_restore_scripts_dir_defined(self):
        with self.assertRaises(SystemExit):
            restore.restore_data("test")

    @patch("os.environ", {"IMAGE_RESTORE_SCRIPTS_DIR": "test"})
    def test_restore_data_backup_is_not_running_restore_scripts_dir_is_not_valid(self):
        with self.assertRaises(SystemExit):
            restore.restore_data("test")

    @patch("os.path.exists")
    @patch("os.environ", {"IMAGE_RESTORE_SCRIPTS_DIR": "test"})
    def test_restore_data_backup_is_not_running_no_tar_file(self, path_exists_mock):
        path_exists_mock.return_value = True
        with self.assertRaises(tarfile.CompressionError):
            restore.restore_data("test")

    @patch("os.stat")
    @patch("glob.glob")
    @patch("tarfile.open", MagicMock())
    @patch("os.path.exists")
    @patch("os.environ", {"IMAGE_RESTORE_SCRIPTS_DIR": "test"})
    def test_restore_data_backup_is_not_running_valid_tar_file(
        self, path_exists_mock, glob_mock, stat_mock
    ):
        path_exists_mock.return_value = True
        glob_mock.return_value = ["test"]
        stat_mock("test").st_mode = 0o544

        with self.assertRaises(SystemExit):
            restore.restore_data(MagicMock())

    @patch("os.stat")
    @patch("glob.glob")
    @patch("tarfile.open", MagicMock())
    @patch("os.path.exists")
    @patch("os.environ", {"IMAGE_RESTORE_SCRIPTS_DIR": "test"})
    def test_restore_data_backup_is_not_running_valid_tar_file_not_the_right_script_permission(
        self, path_exists_mock, glob_mock, stat_mock
    ):
        path_exists_mock.return_value = True
        glob_mock.return_value = ["test"]
        stat_mock("test").st_mode = 0o444

        with self.assertRaises(SystemExit):
            restore.restore_data(MagicMock())

    @patch("os.rmdir")
    @patch("subprocess.run")
    @patch("os.stat")
    @patch("glob.glob")
    @patch("tarfile.open", MagicMock())
    @patch("os.path.exists")
    @patch("os.environ", {"IMAGE_RESTORE_SCRIPTS_DIR": "test"})
    def test_restore_data_backup_is_not_running_valid_tar_file_subprocess_successful(
        self, path_exists_mock, glob_mock, stat_mock, subprocess_run_mock, rmdir_mock
    ):
        path_exists_mock.return_value = True
        glob_mock.return_value = ["test"]
        stat_mock("test").st_mode = 0o544
        subprocess_run_mock.return_value.returncode = 0

        restore.restore_data(MagicMock())
        self.assertIn(str("[call('/tmp/"), str(rmdir_mock.mock_calls))

    @patch("subprocess.run")
    @patch("os.stat")
    @patch("glob.glob")
    @patch("tarfile.open", MagicMock())
    @patch("os.path.exists")
    @patch("os.environ", {"IMAGE_RESTORE_SCRIPTS_DIR": "test"})
    def test_restore_data_backup_is_not_running_valid_tar_file_subprocess_tmp_dir_not_exists(
        self, path_exists_mock, glob_mock, stat_mock, subprocess_run_mock
    ):
        path_exists_mock.return_value = [True, False]
        glob_mock.return_value = ["test"]
        stat_mock("test").st_mode = 0o544
        subprocess_run_mock.return_value.returncode = 0

        with self.assertRaises(SystemExit):
            restore.restore_data(MagicMock())


if __name__ == "__main__":
    main()
