#!/usr/bin/python3

import importlib.util
import os
import sys

spec = importlib.util.spec_from_file_location("module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py")
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

if len(utils.get_env_variable("RELEASE_WATCHER_GIT_TOKEN")) == 0:
    sys.stdout.write("No secret for GiT_TOKEN provided! Exiting ...;")
    sys.exit(1)

if len(utils.get_env_variable("SLACK_WEBHOCK_URL")) == 0:
    sys.stdout.write("No secret for SLACK_WEBHOCK_URL provided! Exiting ...;")
    sys.exit(1)
