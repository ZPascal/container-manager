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

result = 0

if (
    len(utils.get_env_variable("IMAGE_CRON_ENABLED")) != 0
    and int(utils.get_env_variable("IMAGE_CRON_ENABLED")) == 1
):
    # Check if crond process is running
    result = utils.is_supervisor_process_running("crond")

    if result:
        sys.stderr.write(
            "Cron is enabled but crond process (cron) is not running! Restart crond;"
        )
        response = utils.restart_process("crond")

        if response is not None:
            result = 1
    else:
        sys.stdout.write("Cron is running!;")

if (
    utils.get_env_variable("LOGGING_REDIS_HOST") is not None
    and len(utils.get_env_variable("LOGGING_REDIS_HOST")) != 0
):
    # Check if filebeat process is running
    result = utils.is_supervisor_process_running("filebeat")

    if result:
        sys.stderr.write(
            "Logging to Redis enabled but filebeat is not running! Restart filebeat;"
        )
        response = utils.restart_process("filebeat")

        if response is not None:
            result = 1
    else:
        sys.stdout.write("filebeat is running!;")

sys.exit(result)
