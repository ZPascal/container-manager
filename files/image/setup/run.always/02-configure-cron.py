#!/usr/bin/python3

import importlib.util
import subprocess
import os
import sys

# Import utils
spec = importlib.util.spec_from_file_location(
    "module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py"
)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

# Update the cron configuration. If crond is enabled or not, specified by the cron env variable
if int(utils.get_env_variable("IMAGE_CRON_ENABLED")) == 1:
    sys.stdout.write("Cron enabled, setting up autostart for supervisor service;")

    cmd = (
        f"sed -i 's/autostart = .*/autostart = true/g' "
        f"{utils.get_env_variable('IMAGE_SUPERVISOR_DIR')}{os.sep}conf.d{os.sep}00-crond.conf"
    )
    ps = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    if ps.returncode is not None:
        sys.stderr.write(
            f"Error, can't update the "
            f"{utils.get_env_variable('IMAGE_SUPERVISOR_DIR')}{os.sep}conf.d{os.sep}00-crond.conf;"
        )
        sys.exit(1)
else:
    sys.stdout.write("Cron disabled;")

    cmd = (
        f"sed -i 's/autostart = .*/autostart = false/g' "
        f"{utils.get_env_variable('IMAGE_SUPERVISOR_DIR')}{os.sep}conf.d{os.sep}00-crond.conf"
    )
    ps = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    if ps.returncode is not None:
        sys.stderr.write(
            f"Error, can't update the "
            f"{utils.get_env_variable('IMAGE_SUPERVISOR_DIR')}{os.sep}conf.d{os.sep}00-crond.conf;"
        )
        sys.exit(1)
