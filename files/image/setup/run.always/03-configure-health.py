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
if (
    len(utils.get_env_variable("HEALTH_LIVENESS_FORCE_REBOOT")) != 0
    and len(utils.get_env_variable("HEALTH_READINESS_CHECK_ENABLE")) != 0
):
    os.chmod(utils.get_env_variable("IMAGE_CRON_DIR"), 0o775)

    f = open(f"{utils.get_env_variable('IMAGE_CRON_DIR')}{os.sep}kubernetes", "a")
    f.write(
        f"{utils.get_env_variable('IMAGE_HEALTH_CRON')} . "
        f"{utils.get_env_variable('IMAGE_HEALTH_DIR')}{os.sep}check-liveness.py 2>&1 "
        f"{utils.get_env_variable('IMAGE_HEALTH_LIVENESS_LOG')}"
    )
    f.write(
        f"{utils.get_env_variable('IMAGE_HEALTH_CRON')} . "
        f"{utils.get_env_variable('IMAGE_HEALTH_DIR')}{os.sep}check-readiness.py 2>&1 "
        f"{utils.get_env_variable('IMAGE_HEALTH_READINESS_LOG')}"
    )
    f.close()

    os.chmod(utils.get_env_variable("IMAGE_CRON_DIR"), 0o555)
else:
    sys.stdout.write("Health check disabled;")