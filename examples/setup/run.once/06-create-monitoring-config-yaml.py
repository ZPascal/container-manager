#!/usr/bin/python3

import yaml
import importlib.util
import os

spec = importlib.util.spec_from_file_location(
    "module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py"
)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

dictionary = {
    "server_user": f"{utils.get_env_variable('MONGO_INITDB_MONITORING_USERNAME')}",
    "server_password": f"{utils.get_env_variable('MONGO_INITDB_MONITORING_PASSWORD')}",
}

f = open(
    f"{utils.get_env_variable('STORAGE_CONF_DIR')}{os.sep}monitoring-mongodb-config.yaml",
    "w",
)
f.write(yaml.dump(dictionary))
