#!/usr/bin/python3

import json
import importlib.util
import os

spec = importlib.util.spec_from_file_location(
    "module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py"
)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

dictionary = {
    "user": f"{utils.get_env_variable('MONGO_INITDB_ROOT_USERNAME')}",
    "pwd": f"{utils.get_env_variable('MONGO_INITDB_ROOT_PASSWORD')}",
    "roles": ["userAdminAnyDatabase"],
}
f = open(
    f"{utils.get_env_variable('STORAGE_CONF_DIR')}{os.sep}create-admin-account.js", "w"
)
f.write(f"db.createUser({json.dumps(dictionary)})\n")
f.write("quit()")
