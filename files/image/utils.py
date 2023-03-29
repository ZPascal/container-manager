#!/usr/bin/python3

import datetime
import os
import subprocess
import sys
import re


def write_log(log_level: str, logger: str, message: str):
    """The method includes a functionality to write centralized log message to the terminal. It also added a timestamp \
    to the output

    Keyword arguments:
    log_level -> Specifies the log level e.g. ERROR of the output message
    logger -> Specifies the logger name of the output message
    message -> Specifies the log message
    """

    time_stamp = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
    logger = f"\033[1;37m{logger}\033[0m"

    if log_level.lower() == "error":
        log_level = "\033[1;31mERROR\033[0m"
    elif log_level.lower() == "warn":
        log_level = "\033[1;33mWARN\033[0m"
    elif log_level.lower() == "info":
        log_level = "\033[1;32mINFO\033[0m"
    else:
        log_level = f"\033[1;37m{log_level}\033[0m"

    print(f"{time_stamp}\t{log_level}\t{logger} {message}")


def _log_preparation(result_str: str, script: str):
    """The method includes a functionality to prepare the log output and remove predefined characters from the input \
    string. The functionality also iterate over line breaks and reformat the output

    Keyword arguments:
    result_str -> Specifies the input message
    script -> Specifies the executed script
    """

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


def is_process_running(process_name: str) -> bool:
    """The method includes a functionality to check if a process is running or not

    Keyword arguments:
    process_name -> Specify the process name
    """

    command: str = f"ps | grep -v grep | grep {process_name}"
    result_stdout, result_stderr = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    ).communicate()

    if len(result_stdout) == 0:
        return False

    return True


def is_supervisor_process_running(process_name: str) -> bool:
    """The method includes a functionality to check if a supervisord process is running or not

    Keyword arguments:
    process_name -> Specify the process name
    """

    result = False

    with open(f"/tmp/supervisor.{process_name}.state", "r") as f:
        if f.readline() == "RUNNING":
            result = True

    return result


def is_backup_running() -> bool:
    """The method includes a functionality to check if a backup process is running or not"""

    result: bool = is_process_running("{backup.py}")

    return result


def restart_process(process_name: str):
    """The method includes a functionality to restart a supervisord process

    Keyword arguments:
    process_name -> Specify the process name
    """

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


def get_env_variable(variable: str) -> str:
    """The method includes a functionality to get an environment variable

    Keyword arguments:
    variable -> Specify the name of environment variable
    """

    result = os.environ.get(variable)

    if result == "" or result is None:
        return ""
    else:
        return result


def execute_scripts(scripts: list, temp_dir_path: str = ""):
    """The method includes a functionality execute a list of scripts and check if the file permission is correct

    Keyword arguments:
    scripts -> Specify the inserted list of scripts
    temp_dir_path -> Specify an optional temporary directory
    """

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


def set_permissions_recursive(path: str, mode: int):
    """The method includes a functionality to sets the permissions recursive for a folder path

    Keyword arguments:
    path -> Specify the corresponding path as string
    mode -> Specify the access mode as number
    """

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


def extract_dir_env_vars() -> list:
    """The method includes a functionality to extract all directory environment variables from the environment file \
    and returned it as a list"""

    matched_values: list = list()

    with open(f"{get_env_variable('IMAGE_CONFIG_DIR')}{os.sep}env", "r") as file_read:
        lines_read = file_read.readlines()

    pattern = "_DIR="

    for line_local in lines_read:
        if re.search(pattern, line_local):
            matched_values.append(line_local)

    return matched_values
