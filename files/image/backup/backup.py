#!/usr/bin/python3

import importlib.util
import datetime
import glob
import os
import sys
import tarfile
import tempfile

# Import utils
spec = importlib.util.spec_from_file_location(
    "module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py"
)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

# Starts the backup script
utils.write_log("info", os.path.basename(__file__), "Starting backup")

if len(utils.get_env_variable("IMAGE_BACKUP_SCRIPTS_DIR")) != 0 and os.path.exists(
    utils.get_env_variable("IMAGE_BACKUP_SCRIPTS_DIR")
):
    utils.write_log(
        "error",
        os.path.basename(__file__),
        f"Backup script directory is configured properly (IMAGE_BACKUP_SCRIPTS_DIR = "
        f"{utils.get_env_variable('IMAGE_BACKUP_SCRIPTS_DIR')})! "
        f"Set correct value to IMAGE_BACKUP_SCRIPTS_DIR environment variable!",
    )
    sys.exit(1)

utils.write_log(
    "info",
    os.path.basename(__file__),
    f"Script directory is {utils.get_env_variable('IMAGE_BACKUP_SCRIPTS_DIR')}",
)

if len(utils.get_env_variable("STORAGE_BACKUP_DIR")) != 0 and os.path.exists(
    utils.get_env_variable("STORAGE_BACKUP_DIR")
):
    utils.write_log(
        "error",
        os.path.basename(__file__),
        f"Target backup directory is configured properly (STORAGE_BACKUP_DIR = "
        f"{utils.get_env_variable('STORAGE_BACKUP_DIR')})! "
        f"Set correct value to STORAGE_BACKUP_DIR environment variable!",
    )
    sys.exit(1)

utils.write_log(
    "info",
    os.path.basename(__file__),
    f"Target directory is {utils.get_env_variable('STORAGE_BACKUP_DIR')}",
)

temp_dir = tempfile.mkdtemp()
backup_timestamp = datetime.datetime.now().astimezone().strftime("%Y-%m-%d_%H:%M:%S")
backup_temp_dir = f"{temp_dir}{os.sep}backup-{backup_timestamp}"
backup_file_name = f"backup-{backup_timestamp}.tar.gz"

os.makedir(backup_temp_dir)

utils.write_log(
    "info",
    os.path.basename(__file__),
    f"Temporary directory for backup is {backup_temp_dir}",
)

utils.write_log("info", os.path.basename(__file__), "Running backup scripts ...")

image_backup_scripts = sorted(
    glob.glob(f"{utils.get_env_variable('IMAGE_BACKUP_SCRIPTS_DIR')}{os.sep}*.py")
)
utils.execute_scripts(image_backup_scripts, backup_temp_dir)

utils.write_log(
    "info",
    os.path.basename(__file__),
    f"Creating TAR archive with backup - "
    f"{utils.get_env_variable('STORAGE_BACKUP_DIR')}"
    f"{os.sep}{backup_file_name}",
)

# Create a backup tar
tar = tarfile.open(
    f"{utils.get_env_variable('STORAGE_BACKUP_DIR')}{os.sep}{backup_file_name}", "w:gz"
)
tar.add(backup_temp_dir.split(os.sep)[-1], path=temp_dir)
tar.close()

utils.write_log("info", os.path.basename(__file__), "Preparing for backup rotation")

if len(utils.get_env_variable("IMAGE_BACKUP_RETENTION")) != 0:
    image_backup_retention = int(utils.get_env_variable("IMAGE_BACKUP_RETENTION"))

    if 0 <= image_backup_retention <= 9:
        utils.write_log(
            "warn",
            os.path.basename(__file__),
            f"Backup retention was not configured for this image (IMAGE_BACKUP_RETENTION = "
            f"{utils.get_env_variable('IMAGE_BACKUP_RETENTION')}). "
            f"Keeping all backups without rotation!",
        )
    else:
        utils.write_log(
            "info",
            os.path.basename(__file__),
            f"Backup retention configured to {utils.get_env_variable('IMAGE_BACKUP_RETENTION')}",
        )

        current_count = len(
            glob.glob(
                f"{utils.get_env_variable('STORAGE_BACKUP_DIR')}{os.sep}backup-*.tar.gz"
            )
        )

        if current_count >= image_backup_retention:
            oldest_backups = sorted(
                glob.glob(
                    f"{utils.get_env_variable('STORAGE_BACKUP_DIR')}{os.sep}backup-*.tar.gz"
                ),
                key=os.path.getmtime,
            )[-image_backup_retention + 1 : -1]

            for backup_file in oldest_backups:
                utils.write_log(
                    "info", os.path.basename(__file__), f"Deleting backup {backup_file}"
                )
                os.remove(backup_file)
        else:
            utils.write_log(
                "info",
                os.path.basename(__file__),
                f"Found ${current_count} backups. The count is lower or equal to retention count.",
            )

utils.write_log("info", os.path.basename(__file__), "Cleaning up")

os.rmdir(temp_dir)

utils.write_log("info", os.path.basename(__file__), "Backup done")
