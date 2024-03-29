import io
import os
import shutil
import tempfile
from supervisor.xmlrpc import RPCError
from unittest import TestCase, main
from unittest.mock import MagicMock, patch, call, mock_open, Mock

from utils import Utils
from files.image import utils


class UtilsTestCase(TestCase):
    @patch("files.image.utils.write_log")
    def test_log_preparation(self, write_log_mock):
        result_str: str = "result\nresult"
        script: str = "script"
        utils._log_preparation(result_str, script)
        self.assertEqual(
            [
                call(
                    "error",
                    "utils.py",
                    "Error, please check the script: script, ERR: result\nresult",
                )
            ],
            write_log_mock.mock_calls,
        )

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_write_log_error(self, print_mock):
        log_level_list: list = ["error", "warn", "info", ""]
        logger: str = "logger"
        message: str = "message"

        for log_level in log_level_list:
            utils.write_log(log_level, logger, message)
            self.assertIn(log_level.upper(), print_mock.getvalue())

    @patch("subprocess.Popen.communicate")
    def test_is_process_running_true(self, subprocess_run_mock):
        subprocess_run_mock.return_value = ("test", None)

        self.assertEqual(True, utils.is_process_running("test"))

    def test_is_process_running_false(self):
        self.assertEqual(False, utils.is_process_running("test123456"))

    @patch("builtins.open", new_callable=mock_open, read_data="RUNNING")
    def test_is_supervisor_process_running_true(self, open_mock):
        self.assertEqual(True, utils.is_supervisor_process_running("test"))

    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_is_supervisor_process_running_false(self, open_mock):
        self.assertEqual(False, utils.is_supervisor_process_running("test"))

    @patch("files.image.utils.is_process_running")
    def test_is_backup_running_true(self, is_process_running_mock):
        is_process_running_mock.return_value = True
        self.assertEqual(True, utils.is_backup_running())

    @patch("files.image.utils.is_process_running")
    def test_is_backup_running_false(self, is_process_running_mock):
        is_process_running_mock.return_value = False
        self.assertEqual(False, utils.is_backup_running())

    def test_restart_process_empty_process_name(self):
        self.assertEqual("error", utils.restart_process(""))

    def test_restart_process_valid_process_wrong_process_name(self):
        result = utils.restart_process("", 1)
        self.assertEqual("error", result)

    @patch("xmlrpc.client.ServerProxy")
    def test_restart_process_valid_process_error(self, xmlrpc_mock):
        mock: Mock = Mock()
        mock.supervisor.stopProcess = MagicMock()
        mock.supervisor.startProcess = MagicMock(return_value=False)
        xmlrpc_mock.return_value = mock
        result = utils.restart_process("test", 1)
        self.assertEqual(False, result)

    @patch("xmlrpc.client.ServerProxy")
    def test_restart_process_valid_process_stop_issue(self, xmlrpc_mock):
        mock: Mock = Mock()
        mock.supervisor.stopProcess = MagicMock(side_effect=RPCError("test"))
        xmlrpc_mock.return_value = mock
        result = utils.restart_process("test", 1)
        self.assertEqual(None, result)

    @patch("xmlrpc.client.ServerProxy")
    def test_restart_process_valid_process_start_issue(self, xmlrpc_mock):
        mock: Mock = Mock()
        mock.supervisor.stopProcess = MagicMock()
        mock.supervisor.startProcess = MagicMock(side_effect=RPCError("test"))
        xmlrpc_mock.return_value = mock
        result = utils.restart_process("test", 1)
        self.assertEqual(None, result)

    @patch("xmlrpc.client.ServerProxy")
    def test_restart_process_valid_process(self, xmlrpc_mock):
        mock: Mock = Mock()
        mock.supervisor.stopProcess = MagicMock()
        mock.supervisor.startProcess = MagicMock(return_value=True)
        xmlrpc_mock.return_value = mock
        self.assertEqual(True, utils.restart_process("test", 1))

    @patch.dict(os.environ, {"TEST": "test"})
    def test_get_env_variable(self):
        self.assertEqual("test", utils.get_env_variable("TEST"))

    @patch("subprocess.run")
    def test_execute_scripts_no_temp_dir_path(self, subprocess_run_mock):
        subprocess_run_mock.return_value.stdout = b"test"
        self.assertEqual(None, utils.execute_scripts([MagicMock(), MagicMock()]))

    @patch("subprocess.run")
    def test_execute_scripts_temp_dir_path(self, subprocess_run_mock):
        subprocess_run_mock.return_value.stdout = b"test"
        self.assertEqual(
            None, utils.execute_scripts([MagicMock(), MagicMock()], "test")
        )

    @patch("subprocess.run")
    def test_execute_scripts_temp_dir_path_traceback_error(self, subprocess_run_mock):
        subprocess_run_mock.return_value.stdout = b"Traceback"
        with self.assertRaises(SystemExit):
            utils.execute_scripts([MagicMock(), MagicMock()], "test")

    def test_execute_scripts_executed_script_wrong_file_permissions(self):
        test_file: str = f"{Utils._get_path_name()}{os.sep}resources{os.sep}test.py"
        os.chmod(test_file, 0o444)

        with self.assertRaises(SystemExit):
            utils.execute_scripts([f"{test_file}"], "test")

    @patch("subprocess.run")
    def test_execute_scripts_multi_line_output_error(self, subprocess_run_mock):
        subprocess_run_mock.return_value.stdout = b"test;test"
        with self.assertRaises(SystemExit):
            utils.execute_scripts([MagicMock(), MagicMock()])

    @patch("subprocess.run")
    def test_execute_scripts_multi_line_output_info(self, subprocess_run_mock):
        subprocess_run_mock.return_value.stdout = b"test;test"
        subprocess_run_mock.return_value.returncode = 0

        self.assertEqual(None, utils.execute_scripts([MagicMock(), MagicMock()]))

    def test_set_permissions_recursive(self):
        source_test_folder: str = (
            f"{Utils._get_path_name()}{os.sep}resources{os.sep}test"
        )
        destination_test_folder: str = (
            f"{tempfile.gettempdir()}{os.sep}resources{os.sep}test"
        )

        shutil.copytree(source_test_folder, destination_test_folder)

        utils.set_permissions_recursive(destination_test_folder, 0o544)

        self.assertEqual(
            544,
            int(
                str(oct(os.stat(f"{destination_test_folder}{os.sep}test.py").st_mode))[
                    -3:
                ]
            ),
        )

        os.chmod(destination_test_folder, 0o755)
        utils.set_permissions_recursive(destination_test_folder, 0o755)
        shutil.rmtree(destination_test_folder)

    @patch(
        "os.environ", {"IMAGE_CONFIG_DIR": f"{Utils._get_path_name()}{os.sep}resources"}
    )
    def test_extract_dir_env_vars(self):
        self.assertEqual(
            ["TEST_DIR=test\n", "TEST1_DIR=test\n"], utils.extract_dir_env_vars()
        )

    def test_extract_dir_env_vars_no_file(self):
        with self.assertRaises(FileNotFoundError):
            utils.extract_dir_env_vars()


if __name__ == "__main__":
    main()
