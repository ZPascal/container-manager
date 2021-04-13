#!/usr/bin/python3

import importlib.util
import os

spec = importlib.util.spec_from_file_location("module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py")
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

os.makedirs(f"{utils.get_env_variable('STORAGE_DATA_DIR')}{os.sep}db")
os.makedirs(f"{utils.get_env_variable('STORAGE_DATA_DIR')}{os.sep}db-export")
os.makedirs(f"{utils.get_env_variable('STORAGE_DATA_DIR')}{os.sep}db-import")
