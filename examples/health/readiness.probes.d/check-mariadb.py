#!/usr/bin/python3

import importlib.util
import os
import sys

import mariadb

spec = importlib.util.spec_from_file_location(
    "module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py"
)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

result_local: int = 1
is_process_running: bool = utils.is_supervisor_process_running("app")

if is_process_running is True:
    sys.stdout.write("Trying to call the database;")

    try:
        sys.stdout.write("Create a MariaDB connection;")
        conn_params = {
            "user": utils.get_env_variable("MARIADB_INITDB_MONITORING_USERNAME"),
            "password": utils.get_env_variable("MARIADB_INITDB_MONITORING_PASSWORD"),
            "host": utils.get_env_variable("MARIADB_INITDB_HOST"),
            "port": int(utils.get_env_variable('MARIADB_INITDB_PORT')),
            "database": "mysql",
            "ssl_ca": f"{utils.get_env_variable('STORAGE_CONF_DIR')}{os.sep}certs{os.sep}ca.crt",
            "ssl_verify_cert": False,
            "unix_socket": "/tmp/mysqld.sock",
        }

        conn = mariadb.connect(**conn_params)
    except Exception as e:
        sys.stderr.write(f"Can not create the connection. Check the error: {e};")
        sys.exit(1)

    try:
        sys.stdout.write("Create a MariaDB cursor;")
        cur = conn.cursor()
    except Exception as e:
        sys.stderr.write(f"Can not create the cursor. Check the error: {e};")
        sys.exit(1)

    cur.execute("SELECT * FROM user;")
    result = cur.fetchone()
    conn.close()

    if result == "" or result is None or len(result) == 0:
        sys.stderr.write("Main command didn't respond!;")
        if bool(utils.get_env_variable("IMAGE_HEALTH_READINESS_FORCE_REBOOT")):
            response = utils.restart_process("app")
            if response is not None:
                result_local = 1
        else:
            result_local = 1
    else:
        sys.stdout.write("Main command responded successfully;")
        result_local = 0
else:
    sys.stderr.write("App is not running!;")
    if bool(utils.get_env_variable("IMAGE_HEALTH_READINESS_FORCE_REBOOT")):
        sys.stderr.write("App is not running. Performing a reboot;")
        response = utils.restart_process("exporter")

        if response is not True:
            result_local = 1
    else:
        result_local = 1

sys.exit(result_local)
