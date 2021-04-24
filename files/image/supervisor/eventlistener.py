#!/usr/bin/python3

import os
import sys


def _write_file(filename: str, content: str):
    f = open(filename, "w")
    f.write(content)
    f.close()


def _write_pid_file(pid_dir: str, process: str, pid: int):
    _write_file(f"{pid_dir}{os.sep}supervisor.{process}.pid", str(pid))


def _write_state_file(state_dir: str, process: str, state: str):
    _write_file(f"{state_dir}{os.sep}supervisor.{process}.state", state)


def _write_stdout(message_stdout: str):
    # Only eventlistener protocol messages may be sent to stdout
    sys.stdout.write(message_stdout)
    # Use the flush methode to clean the buffer and post ot to the console
    sys.stdout.flush()


def _write_stderr(message_stderr: str):
    sys.stderr.write(message_stderr)
    # Use the flush methode to clean the buffer and post ot to the console
    sys.stderr.flush()


# Write state and the pid inside tmp files
def main():
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
