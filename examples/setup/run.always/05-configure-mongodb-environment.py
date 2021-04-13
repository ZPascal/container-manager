#!/usr/bin/python3

import importlib.util
import os
import sys

spec = importlib.util.spec_from_file_location("module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py")
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

if len(utils.get_env_variable("MONGO_INITDB_ROOT_USERNAME")) == 0:
    sys.stdout.write("No secret for user.root.name provided! Exiting ...;")
    sys.exit(1)

if len(utils.get_env_variable("MONGO_INITDB_ROOT_PASSWORD")) == 0:
    sys.stdout.write("No secret for user.root.password provided! Exiting ...;")
    sys.exit(1)

if len(utils.get_env_variable("MONGO_INITDB_USER_USERNAME")) == 0:
    sys.stdout.write("No secret for user.name provided! Exiting ...;")
    sys.exit(1)

if len(utils.get_env_variable("MONGO_INITDB_USER_PASSWORD")) == 0:
    sys.stdout.write("No secret for user.password provided! Exiting ...;")
    sys.exit(1)
