#!/usr/bin/python3

import importlib.util
import os
import sys

# Import utils
spec = importlib.util.spec_from_file_location(
    "module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py"
)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

# Set backup crontab entries
if int(utils.get_env_variable("IMAGE_BACKUP_ENABLED")) == 1:
    if os.path.exists(f"{utils.get_env_variable('IMAGE_CRON_DIR')}{os.sep}kubernetes"):
        os.chmod(utils.get_env_variable("IMAGE_CRON_DIR"), 0o775)
        os.remove(f"{utils.get_env_variable('IMAGE_CRON_DIR')}{os.sep}kubernetes")

    sys.stdout.write("Backup enabled, creating crontab entry for backup;")

    with open(f"{utils.get_env_variable('IMAGE_CRON_DIR')}{os.sep}kubernetes", "w") as f:
        f.write(
            f"{utils.get_env_variable('IMAGE_BACKUP_CRON')} "
            f"{utils.get_env_variable('IMAGE_CONFIG_DIR')}{os.sep}env; "
            f"{utils.get_env_variable('IMAGE_BACKUP_DIR')}{os.sep}backup.py 2>&1 "
            f">{utils.get_env_variable('IMAGE_BACKUP_LOG')}\n"
        )
else:
    sys.stdout.write("Backup disabled;")
