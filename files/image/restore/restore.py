#!/usr/bin/python3

import importlib.util
import datetime
import glob
import os
import subprocess
import sys
import tarfile
import tempfile

# Import utils
spec = importlib.util.spec_from_file_location(
    "module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py"
)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)


def restore_data(backup_file: str):
    """The method includes a functionality to restore the backup data and unpack the archive file

    Keyword arguments:
    backup_file -> Specify the backup archive file
    """

    if backup_file == "":
        utils.write_log(
            "error",
            os.path.basename(__file__),
            "No backup file specified to restore data from! Call restore script with specified filename!",
        )
        sys.exit(1)

    if utils.is_backup_running():
        utils.write_log(
            "error",
            os.path.basename(__file__),
            "Backup is running. Restoring is not possible",
        )
        sys.exit(1)
    else:
        utils.write_log("info", os.path.basename(__file__), "Starting restore")

        if (
            utils.get_env_variable("IMAGE_RESTORE_SCRIPTS_DIR") == ""
            or os.path.exists(utils.get_env_variable("IMAGE_RESTORE_SCRIPTS_DIR"))
            is False
        ):
            utils.write_log(
                "error",
                os.path.basename(__file__),
                f"Restore script directory is configured properly (IMAGE_RESTORE_SCRIPTS_DIR = "
                f"{utils.get_env_variable('IMAGE_RESTORE_SCRIPTS_DIR')})! "
                f"Set correct value to IMAGE_RESTORE_SCRIPTS_DIR environment variable!",
            )
            sys.exit(1)

        utils.write_log(
            "info",
            os.path.basename(__file__),
            f"Script directory is {utils.get_env_variable('IMAGE_RESTORE_SCRIPTS_DIR')}",
        )
        utils.write_log(
            "info",
            os.path.basename(__file__),
            f"Target directory is {utils.get_env_variable('STORAGE_BASE_DIR')}",
        )

        temp_dir = tempfile.mkdtemp()
        restore_timestamp = (
            datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
        )

        utils.write_log(
            "info",
            os.path.basename(__file__),
            f"Extracting backup archive {backup_file} at {restore_timestamp}",
        )
        tar = tarfile.open(backup_file, "r:tar.gz")
        for tarinfo in tar:
            tar.extract(tarinfo, temp_dir)
        tar.close()

        restore_temp_dir = os.listdir(temp_dir)

        utils.write_log(
            "info",
            os.path.basename(__file__),
            f"Temporary directory for restore is {restore_temp_dir}",
        )

        utils.write_log(
            "info", os.path.basename(__file__), "Running restore scripts ..."
        )

        restore_scripts = sorted(
            glob.glob(
                f"{utils.get_env_variable('IMAGE_RESTORE_SCRIPTS_DIR')}{os.sep}*.py"
            )
        )

        for script in restore_scripts:
            oct_perm: str = str(oct(os.stat(script).st_mode))[-3:]
            if int(oct_perm) >= 544:
                utils.write_log(
                    "info",
                    os.path.basename(__file__),
                    f"Running backup script: {script}",
                )
                command = [
                    f"{script}",
                    "-i",
                    f"{utils.get_env_variable('RESTORE_TEMP_DIR')}",
                ]
                result = subprocess.run(
                    command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                )

                if result.returncode != 0:
                    utils.write_log(
                        "error",
                        os.path.basename(__file__),
                        f"Error, please check the script: {script}, ERR: {result.stdout}",
                    )
                    sys.exit(1)
            else:
                utils.write_log(
                    "error",
                    os.path.basename(__file__),
                    f"Wrong permissions. Please, upgrade the permissions higher than oct 544: {script}",
                )
                sys.exit(1)

        utils.write_log("info", os.path.basename(__file__), "Cleaning up")

        if os.path.exists(temp_dir) is True:
            os.rmdir(temp_dir)
            utils.write_log("info", os.path.basename(__file__), "Restore done")
        else:
            utils.write_log("error", os.path.basename(__file__), "Temp path not exists")
            sys.exit(1)
