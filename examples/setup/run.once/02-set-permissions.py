#!/usr/bin/python3

import importlib.util
import os

spec = importlib.util.spec_from_file_location("module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py")
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

os.chown(f"{utils.get_env_variable('STORAGE_DATA_DIR')}{os.sep}db", 500, 500)
os.chown(f"{utils.get_env_variable('STORAGE_DATA_DIR')}{os.sep}db-export", 500, 500)
os.chown(f"{utils.get_env_variable('STORAGE_DATA_DIR')}{os.sep}db-import", 500, 500)
