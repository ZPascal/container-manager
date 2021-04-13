#!/usr/bin/python3

import importlib.util
import os
import time

spec = importlib.util.spec_from_file_location("module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py")
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

# The MongoDB server was started before and needs a few seconds for the initialization processes.
# We wait a few seconds here.
time.sleep(5)

# Next create admin account
os.system(
    f"mongo {utils.get_env_variable('MONGO_INITDB_ROOT_USERNAME')} "
    f"{utils.get_env_variable('STORAGE_CONF_DIR')}{os.sep}create-admin-account.js")

# Create monitoring account
os.system(
    f"mongo {utils.get_env_variable('MONGO_INITDB_ROOT_USERNAME')} "
    f"{utils.get_env_variable('STORAGE_CONF_DIR')}{os.sep}create-monitoring-account.js "
    f"-u {utils.get_env_variable('MONGO_INITDB_ROOT_USERNAME')} "
    f"-p {utils.get_env_variable('MONGO_INITDB_ROOT_PASSWORD')}")

# Create user account
os.system(
    f"mongo {utils.get_env_variable('MONGO_INITDB_ROOT_USERNAME')} "
    f"{utils.get_env_variable('STORAGE_CONF_DIR')}{os.sep}create-user-account.js "
    f"-u {utils.get_env_variable('MONGO_INITDB_ROOT_USERNAME')} "
    f"-p {utils.get_env_variable('MONGO_INITDB_ROOT_PASSWORD')}")

# Create user collection
os.system(
    f"mongo {utils.get_env_variable('MONGO_INITDB_ROOT_USERNAME')} "
    f"{utils.get_env_variable('STORAGE_CONF_DIR')}{os.sep}create-user-collection.js "
    f"-u {utils.get_env_variable('MONGO_INITDB_USER_USERNAME')} "
    f"-p {utils.get_env_variable('MONGO_INITDB_USER_PASSWORD')} "
    f"--authenticationDatabase {utils.get_env_variable('MONGO_INITDB_NAME')}")
