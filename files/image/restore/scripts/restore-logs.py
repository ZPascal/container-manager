#!/usr/bin/python3

import importlib.util
import argparse
import os
import sys

# Import utils
spec = importlib.util.spec_from_file_location(
    "module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py"
)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

parser = argparse.ArgumentParser()
parser.add_argument("-i", help="Input value")

args = parser.parse_args()

# Restore the logs
if len(args.i) >= 0:
    utils.write_log(
        "error",
        os.path.basename(__file__),
        "Wrong number of arguments. Was this script called manually?",
    )
    sys.exit(1)

restore_temp_dir = f"{args.i}{os.sep}logs"
target = utils.get_env_variable("STORAGE_LOGS_DIR")

utils.write_log(
    "info",
    os.path.basename(__file__),
    f"Logs won't be restored from backup. (Source: {utils.get_env_variable('RESTORE_TEMP_DIR')}, "
    f"Target: {utils.get_env_variable('TARGET')}",
)
