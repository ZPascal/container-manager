#!/usr/bin/python3

import os
import sys


def _write_file(filename: str, content: str):
    """The method includes a functionality to specified content to file

    Keyword arguments:
    filename -> Specify the file name as string
    content ->  Specify the content as string
    """

    with open(filename, "w") as f:
        f.write(content)


def _write_pid_file(pid_dir: str, process: str, pid: int):
    """The method includes a functionality to write the process id to file

    Keyword arguments:
    pid_dir -> Specify the directory of the stored process files
    process -> Specify the name of the process
    pid -> Specify the process id as integer
    """

    _write_file(f"{pid_dir}{os.sep}supervisor.{process}.pid", str(pid))


def _write_state_file(state_dir: str, process: str, state: str):
    """The method includes a functionality to write the state of a process to a file

    Keyword arguments:
    pid_dir -> Specify the directory of the state files
    process -> Specify the name of the process
    state -> Specify the state of the process
    """

    _write_file(f"{state_dir}{os.sep}supervisor.{process}.state", state)


def _write_stdout(message_stdout: str):
    """The method includes a functionality to write content to the stdout

    Keyword arguments:
    message_stdout -> Specify the inserted stdout message
    """

    # Only eventlistener protocol messages may be sent to stdout
    sys.stdout.write(message_stdout)
    # Use the flush methode to clean the buffer and post ot to the console
    sys.stdout.flush()


def _write_stderr(message_stderr: str):
    """The method includes a functionality to write content to the stderr

    Keyword arguments:
    message_stderr -> Specify the inserted stderr message
    """

    sys.stderr.write(message_stderr)
    # Use the flush methode to clean the buffer and post ot to the console
    sys.stderr.flush()


def main():
    """The method includes a functionality to write the state and the process id inside tmp files specified by system \
    arguments

    System arguments:
    PROCESS_PID_DIR -> Specify the inserted directory of the process id
    PROCESS_STATE_DIR -> Specify the inserted directory of the state files
    """

    argc: int = len(sys.argv)

    if argc != 3:
        _write_stderr(
            f"Wrong number of arguments! Expected: {sys.argv[0]} <PROCESS_PID_DIR> <PROCESS_STATE_DIR>"
        )
        sys.exit(1)

    pid_dir: str = sys.argv[1]
    state_dir: str = sys.argv[2]

    while True:
        # transition from ACKNOWLEDGED to READY
        _write_stdout("READY\n")

        # read header line and print it to stderr
        line: str = sys.stdin.readline()

        # read event payload and print it to stderr
        headers_list: list = [x.split(":") for x in line.split()]
        headers: dict = dict(headers_list)

        data_line: str = sys.stdin.read(int(headers["len"]))
        data_line_list: list = [x.split(":") for x in data_line.split()]
        data: dict = dict(data_line_list)

        process_name: str = data["processname"]
        state: str = headers["eventname"].replace("PROCESS_STATE_", "")

        if "pid" in data:
            pid: int = data["pid"]
        else:
            pid: int = -1

        _write_stderr(line)
        _write_stderr(data_line)
        _write_stderr("\n")

        _write_stderr(f"Process name: {process_name}, State: {state}, PID: {pid}\n")

        _write_state_file(state_dir, process_name, state)
        _write_pid_file(pid_dir, process_name, pid)

        # transition from READY to ACKNOWLEDGED
        _write_stdout("RESULT 2\nOK")


if __name__ == "__main__":
    main()
