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

# Update the filebeat configuration. If filebeat is enabled or not, specified by the redis host env variable
if (
    utils.get_env_variable("LOGGING_REDIS_HOST") is not None
    and len(utils.get_env_variable("LOGGING_REDIS_HOST")) != 0
):
    sys.stdout.write("Redis host specified - enabling filebeat;")

    cmd = (
        f"sed -i 's/autostart = .*/autostart = true/g' "
        f"{utils.get_env_variable('IMAGE_SUPERVISOR_DIR')}{os.sep}conf.d{os.sep}01-filebeat.conf"
    )
    ps = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    if ps.returncode is not None:
        sys.stderr.write(
            f"Error, can't update the "
            f"{utils.get_env_variable('IMAGE_SUPERVISOR_DIR')}{os.sep}conf.d{os.sep}01-filebeat.conf;"
        )
        sys.exit(1)
else:
    sys.stdout.write("Redis host not specified - disabling filebeat;")

    cmd = (
        f"sed -i 's/autostart = .*/autostart = false/g' "
        f"{utils.get_env_variable('IMAGE_SUPERVISOR_DIR')}{os.sep}conf.d{os.sep}01-filebeat.conf"
    )
    ps = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    if ps.returncode is not None:
        sys.stderr.write(
            f"Error, can't update the "
            f"{utils.get_env_variable('IMAGE_SUPERVISOR_DIR')}{os.sep}conf.d{os.sep}01-filebeat.conf;"
        )
        sys.exit(1)
