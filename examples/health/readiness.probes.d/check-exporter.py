#!/usr/bin/python3

import importlib.util
import os
import sys
import subprocess

spec = importlib.util.spec_from_file_location(
    "module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py"
)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

result_local = utils.is_supervisor_process_running("exporter")

if result_local == 0:
    sys.stdout.write("Trying to call main page at localhost:9187/health;")

    command = [
        "curl",
        "-s",
        "-o",
        "/dev/null",
        "-w",
        "%{http_code}",
        "localhost:9187/health",
    ]
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    )

    if result != 0:
        sys.stderr.write("Main page didn't respond!;")
        if bool(utils.get_env_variable("IMAGE_HEALTH_LIVENESS_FORCE_REBOOT")):
            response = utils.restart_process("exporter")

            if response is not None:
                result_local = 1
        else:
            result_local = 1
    else:
        sys.stdout.write(f"Main page responded with HTTP Status {result.stdout}")
        if 200 <= int(result.stdout) <= 400:
            result_local = 0
        else:
            sys.stderr.write("Main page could not be called.;")
            if bool(utils.get_env_variable("IMAGE_HEALTH_LIVENESS_FORCE_REBOOT")):
                response = utils.restart_process("exporter")

                if response is not None:
                    result_local = 1
            else:
                result_local = 1
else:
    sys.stderr.write("Exporter is not running!;")

sys.exit(result_local)
