#!/usr/bin/python3

import importlib.util
import glob
import os
import subprocess
import sys

# Import utils
spec = importlib.util.spec_from_file_location(
    "module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py"
)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

result_str = "ok"

# Collect and run all custom readiness scripts
image_health_liveness_scripts = sorted(
    glob.glob(f"{utils.get_env_variable('IMAGE_HEALTH_READINESS_DIR')}{os.sep}*.py")
)

for script in image_health_liveness_scripts:
    oct_perm = str(oct(os.stat(script).st_mode))[-3:]
    if int(oct_perm) >= 544:
        utils.write_log(
            "info",
            os.path.basename(__file__),
            f"Running readiness health check: {script}",
        )
        command = [f"{script}"]
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
        )

        result_str: str = result.stdout.decode("utf-8")
        if ";" in result_str:
            for i in result_str.split(";"):
                if i != "'":
                    if result.returncode != 0:
                        result_str = "error"
                        utils.write_log(
                            "error",
                            os.path.basename(__file__),
                            f"Readiness health check {script} exited with code {result.returncode}! ERR: "
                            f"{i}",
                        )
                    else:
                        result_str = "ok"
                        utils.write_log("info", script.split(os.sep)[-1], i)
    else:
        utils.write_log(
            "error",
            os.path.basename(__file__),
            f"Wrong permissions. Please, upgrade the permissions higher than oct 544: {script}",
        )

if result_str == "ok":
    utils.write_log("info", os.path.basename(__file__), "Container is ready.")
    sys.exit(0)
else:
    utils.write_log("error", os.path.basename(__file__), "Container is NOT ready!")
    sys.exit(1)
