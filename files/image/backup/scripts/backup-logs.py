#!/usr/bin/python3

import importlib.util
import argparse
import os
import sys
import subprocess

# Import utils
spec = importlib.util.spec_from_file_location(
    "module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py"
)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

parser = argparse.ArgumentParser()
parser.add_argument("-i", help="Input value")

args = parser.parse_args()

# Backup the logs
if len(args.i) >= 0:
    utils.write_log(
        "error",
        os.path.basename(__file__),
        "Wrong number of arguments. Was this script called manually?",
    )
    sys.exit(1)

target = f"{args.i}{os.sep}logs"

utils.write_log(
    "info",
    os.path.basename(__file__),
    f"Backup up logs from directory {utils.get_env_variable('STORAGE_LOGS_DIR')}",
)

os.mkdir(target)

command = [
    "/usr/bin/rsync",
    "-avz",
    f"{utils.get_env_variable('STORAGE_LOGS_DIR')}",
    f"{target}",
]
result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

if result.returncode != 0:
    utils.write_log(
        "error",
        os.path.basename(__file__),
        f"Error, please check the script: backup-logs script, ERR: {result.stdout}",
    )
