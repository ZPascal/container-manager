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

result_local = 0

if (
    len(utils.get_env_variable("IMAGE_CRON_ENABLED")) != 0
    and int(utils.get_env_variable("IMAGE_CRON_ENABLED")) == 1
):
    # Check if crond process is running
    result = utils.is_supervisor_process_running("crond")

    if result != 0:
        sys.stdout.write("Cron is enabled but crond process is not running!;")
        result_local = 1
    else:
        sys.stdout.write("Cron is running!;")

if (
    utils.get_env_variable("LOGGING_REDIS_HOST") is not None
    and len(utils.get_env_variable("LOGGING_REDIS_HOST")) != 0
):
    # Check if filebeat process is running
    result = utils.is_supervisor_process_running("filebeat")

    if result != 0:
        sys.stdout.write("Logging to Redis enabled but filebeat is not running!;")
        result_local = 1
    else:
        sys.stdout.write("filebeat is running!;")

sys.exit(result_local)
