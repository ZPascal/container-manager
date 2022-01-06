#!/usr/bin/python3

import datetime
import os
import subprocess
import sys
import re


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


# Format the code, if there's any special log out e.g. exceptions inside the output stream
def _log_preparation(result_str: str, script: str):
    result_str_prep: list = (
        result_str.replace("\\'", '"')
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
def is_process_running(process_name: str) -> bool:
    command: str = f"ps | grep -v grep | grep {process_name}"
    result_stdout, result_stderr = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    ).communicate()

    if len(result_stdout) == 0:
        return False

    return True


# Check if supervisord process running
def is_supervisor_process_running(process_name: str) -> bool:
    result = False

    f = open(f"/tmp/supervisor.{process_name}.state", "r")

    if f.readline() == "RUNNING":
        result = True

    f.close()

    return result


# Check if backup is actual running
def is_backup_running() -> bool:
    result: bool = is_process_running("{backup.py}")

    return result


# Restart the process/ program
def restart_process(process_name: str):
    if len(process_name) != 0:
        command = [
            "supervisorctl",
            "-s",
            "unix:///tmp/supervisord.sock",
            "-c",
            f"{get_env_variable('IMAGE_SUPERVISOR_DIR')}{os.sep}global.conf",
            "restart",
            process_name,
        ]
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
        )

        if result.returncode != 0:
            return result.stdout

        return None
    else:
        write_log(
            "error",
            os.path.basename(__file__),
            "Error, please define a valid process name",
        )
        return "error"


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
        oct_perm: str = str(oct(os.stat(script).st_mode))[-3:]
        if int(oct_perm) >= 544:
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

            result_str: str = result.stdout.decode("utf-8")
            if ";" in result_str:
                result_str_prep: list = result_str.split(";")
                for i in range(0, len(result_str_prep)):
                    if result_str_prep[i] != "'" and result_str_prep[i] != '"':
                        if result.returncode != 0:
                            for j in range(i, len(result_str_prep)):
                                _log_preparation(result_str_prep[j], script)

                            sys.exit(1)
                        else:
                            write_log(
                                "info",
                                script.split(os.sep)[-1],
                                result_str_prep[i]
                                .replace("b'", "")
                                .replace("b", "")
                                .replace('"', ""),
                            )
            elif "Traceback" in result_str:
                _log_preparation(result_str, script)
                sys.exit(1)
        else:
            write_log(
                "error",
                os.path.basename(__file__),
                f"Wrong permissions. Please, upgrade the permissions higher than oct 544: {script}",
            )
            sys.exit(1)


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


# Extract the dirs from the env file
def extract_dir_env_vars() -> list:
    matched_values: list = list()

    file_read = open(f"{get_env_variable('IMAGE_CONFIG_DIR')}{os.sep}env", "r")
    lines_read = file_read.readlines()
    pattern = "_DIR="

    for line_local in lines_read:
        if re.search(pattern, line_local):
            matched_values.append(line_local)

    file_read.close()

    return matched_values
