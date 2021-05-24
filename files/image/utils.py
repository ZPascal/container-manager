#!/usr/bin/python3

import datetime
import os
import subprocess
import sys


# Central logger
def write_log(log_level: str, logger: str, message: str):
    time_stamp = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
    logger = f"\033[1;37m{logger}\033[0m"

    if log_level.lower() == "error":
        log_level = f"\033[1;31mERROR\033[0m"
    elif log_level.lower() == "warn":
        log_level = f"\033[1;33mWARN\033[0m"
    elif log_level.lower() == "info":
        log_level = f"\033[1;32mINFO\033[0m"
    else:
        log_level = f"\033[1;37m{log_level}\033[0m"

    print(f"{time_stamp}\t{log_level}\t{logger} {message}")


# Format the code, if theres any special log out e.g. exceptions inside the output stream
def _log_preparation(result_str: str, script: str):
    result_str_prep: list = (
        result_str.replace("b'", "")
        .replace('b"', "")
        .replace("\\'", '"')
        .replace("'", "")
        .replace('"', "")
        .replace("\t", "")
        .split("\\n")
    )

    for j in range(0, len(result_str_prep)):
        if result_str_prep[j] != "":
            write_log(
                "error",
                os.path.basename(__file__),
                f"Error, please check the script: {script}, ERR: "
                f"{str(result_str_prep[j]).strip()}",
            )


# Check if process is running
def is_process_running(process_name: str):
    command = ["ps", "|", "grep", "-v", "grep", "|", "grep", process_name]
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    )

    return result.stdout


# Check if supervisord process running
def is_supervisor_process_running(process_name: str) -> int:
    result = 1

    f = open(f"/tmp/supervisor.{process_name}.state", "r")

    if f.readline() == "RUNNING":
        result = 0

    return result


# Check if backup is actual running
def is_backup_running():
    result = is_process_running("{backup.py}")

    if len(result) != 0:
        result = True
    else:
        result = False

    return result


# Get the env variable by name
def get_env_variable(variable: str) -> str:
    result = os.environ.get(variable)

    if result == "" or result is None:
        return ""
    else:
        return result


# Execute a list of scripts and check if file permission is correct
def execute_scripts(scripts: list, temp_dir_path: str = ""):
    for script in scripts:
        oct_perm = str(oct(os.stat(script).st_mode))[-3:]
        if int(oct_perm) >= 444:
            if len(temp_dir_path) == 0:
                message = f"* Running setup file {script}"
                command = [f"{script}"]
            else:
                message = f"* Running backup file {script} {temp_dir_path}"
                command = [f"{script}", temp_dir_path]

            write_log("info", os.path.basename(__file__), message)
            result = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )

            result_str = str(result.stdout)
            if ";" in result_str:
                result_str_prep: list = result_str.split(";")
                for i in range(0, len(result_str_prep)):
                    if result_str_prep[i] != "'":
                        if result.returncode != 0:
                            for j in range(i, len(result_str_prep)):
                                _log_preparation(result_str_prep[j], script)

                            sys.exit(1)
                        else:
                            write_log(
                                "info",
                                script.split(os.sep)[-1],
                                result_str_prep[i].replace("b'", ""),
                            )
            elif "Traceback" in result_str:
                _log_preparation(result_str, script)
                sys.exit(1)
        else:
            write_log(
                "error",
                os.path.basename(__file__),
                f"Wrong permissions. Please, upgrade the permissions higher than oct 444: {script}",
            )


# Sets the permissions recursive
def set_permissions_recursive(path: str, mode: int):
    root = None
    files = None

    for root, dirs, files in os.walk(path, topdown=False):
        for dir_path in [os.path.join(root, d) for d in dirs]:
            if "__pycache__" not in dir_path:
                os.chmod(dir_path, mode)

    if root is not None and files is not None:
        for file in [os.path.join(root, f) for f in files]:
            if "__pycache__" not in file:
                os.chmod(file, mode)
