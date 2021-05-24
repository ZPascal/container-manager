
#!/usr/bin/python3

import importlib.util
import os
import sys

import psycopg2

spec = importlib.util.spec_from_file_location(
    "module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py"
)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

result_local = utils.is_supervisor_process_running("app")

if result_local == 0:
    sys.stdout.write("Trying to call the database;")

    try:
        sys.stdout.write("Create a PostgreSQL connection;")
        conn = psycopg2.connect(
            f"user={utils.get_env_variable('POSTGRES_INITDB_MONITORING_USERNAME')} "
            f"password={utils.get_env_variable('POSTGRES_INITDB_MONITORING_PASSWORD')} "
            f"host={utils.get_env_variable('POSTGRES_INITDB_HOST')} "
            f"port={utils.get_env_variable('POSTGRES_INITDB_PORT')} "
            f"dbname=postgres "
            f"ca_cert={utils.get_env_variable('STORAGE_CONF_DIR')}{os.sep}ca.crt sslmode=verify-ca"
        )
    except Exception as e:
        sys.stderr.write(f"Can not create the connection. Check the error: {e};")
        sys.exit(1)

    try:
        sys.stdout.write("Create a PostgreSQL cursor;")
        cur = conn.cursor()
    except Exception as e:
        sys.stderr.write(f"Can not create the cursor. Check the error: {e};")
        sys.exit(1)

    cur.execute("SELECT * FROM postgres;")
    result = cur.fetchone()

    if result != "" or result is not None:
        sys.stderr.write("Main command didn't respond!;")
        if bool(utils.get_env_variable("IMAGE_HEALTH_LIVENESS_FORCE_REBOOT")):
            response = utils.restart_process("app")

            if response is not None:
                result_local = 1
        else:
            result_local = 1
    else:
        sys.stdout.write("Main command responded with error state")
        result_local = 0
else:
    sys.stderr.write("App is not running!;")

sys.exit(result_local)
