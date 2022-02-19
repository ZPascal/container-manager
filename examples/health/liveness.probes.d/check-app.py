#!/usr/bin/python3

import importlib.util
import os
import sys

spec = importlib.util.spec_from_file_location(
    "module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py"
)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

result = utils.is_supervisor_process_running("app")

if result != 0:
    sys.stderr.write("App is not running!;")
    response = utils.restart_process("app")

    if response is not None:
        result = 1

sys.exit(result)
