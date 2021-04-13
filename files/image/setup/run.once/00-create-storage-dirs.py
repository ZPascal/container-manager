#!/usr/bin/python3

import importlib.util
import os

# Import utils
spec = importlib.util.spec_from_file_location(
    "module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py"
)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

# Create all used storage dirs
if not os.path.exists(utils.get_env_variable("STORAGE_BACKUP_DIR")):
    os.makedirs(utils.get_env_variable("STORAGE_BACKUP_DIR"))

if not os.path.exists(utils.get_env_variable("STORAGE_CONF_DIR")):
    os.makedirs(utils.get_env_variable("STORAGE_CONF_DIR"))

if not os.path.exists(utils.get_env_variable("STORAGE_DATA_DIR")):
    os.makedirs(utils.get_env_variable("STORAGE_DATA_DIR"))

if not os.path.exists(utils.get_env_variable("STORAGE_FILEBEAT_DIR")):
    os.makedirs(utils.get_env_variable("STORAGE_FILEBEAT_DIR"))

if not os.path.exists(utils.get_env_variable("STORAGE_FILEBEAT_REG_DIR")):
    os.makedirs(utils.get_env_variable("STORAGE_FILEBEAT_REG_DIR"))

if not os.path.exists(utils.get_env_variable("STORAGE_LOGS_DIR")):
    os.makedirs(utils.get_env_variable("STORAGE_LOGS_DIR"))

if not os.path.exists(utils.get_env_variable("SUPERVISOR_LOGS_DIR")):
    os.makedirs(utils.get_env_variable("SUPERVISOR_LOGS_DIR"))
