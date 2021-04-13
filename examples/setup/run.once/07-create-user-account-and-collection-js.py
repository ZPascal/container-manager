#!/usr/bin/python3

import json
import importlib.util
import os

spec = importlib.util.spec_from_file_location("module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py")
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

dictionary = {
    "user": f"{utils.get_env_variable('MONGO_INITDB_USER_USERNAME')}",
    "pwd": f"{utils.get_env_variable('MONGO_INITDB_USER_PASSWORD')}",
    "roles": [{"role": "readWrite", "db": f"{utils.get_env_variable('MONGO_INITDB_NAME')}"}]
}
o = open(f"{utils.get_env_variable('IMAGE_CONFIG_DIR')}{os.sep}create-db-test-data.js", "r")

f = open(f"{utils.get_env_variable('STORAGE_CONF_DIR')}{os.sep}create-user-account.js", "w")
f.write(f"db = db.getSiblingDB('{utils.get_env_variable('MONGO_INITDB_NAME')}')\n")
f.write(f"db.createUser({json.dumps(dictionary)})\n")
f.write("quit()")

f = open(f"{utils.get_env_variable('STORAGE_CONF_DIR')}{os.sep}create-user-collection.js", "w")
f.write(f"db = db.getSiblingDB('{utils.get_env_variable('MONGO_INITDB_NAME')}')\n")
f.write(f"{o.read()}\n")
f.write("quit()")
