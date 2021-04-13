#!/usr/bin/python3

import sys


def write_file(filename, content):
    f = open(filename, "w")
    f.write(content)
    f.close()


def write_pid_file(pid_dir, process, pid):
    write_file(pid_dir + "/supervisor." + process + ".pid", str(pid))


def write_state_file(state_dir, process, state):
    write_file(state_dir + "/supervisor." + process + ".state", state)


def write_stdout(s):
    # only eventlistener protocol messages may be sent to stdout
    sys.stdout.write(s)
    sys.stdout.flush()


def write_stderr(s):
    sys.stderr.write(s)
    sys.stderr.flush()


# Write state and the pid inside tmp files
def main():
    argc = len(sys.argv)

    if argc != 3:
        write_stdout(
            "Wrong number of arguments! Expected: "
            + sys.argv[0]
            + " <PROCESS_PID_DIR> <PROCESS_STATE_DIR>"
        )
        sys.exit(1)

    pid_dir = sys.argv[1]
    state_dir = sys.argv[2]

    while 1:
        # transition from ACKNOWLEDGED to READY
        write_stdout("READY\n")

        # read header line and print it to stderr
        line = sys.stdin.readline()

        # read event payload and print it to stderr
        headers = dict([x.split(":") for x in line.split()])
        data_line = sys.stdin.read(int(headers["len"]))
        data = dict([x.split(":") for x in data_line.split()])

        process_name = data["processname"]
        state = headers["eventname"].replace("PROCESS_STATE_", "")

        if "pid" in data:
            pid = data["pid"]
        else:
            pid = -1

        write_stderr(line)
        write_stderr(data_line)
        write_stderr("\n")

        write_stderr(
            "Process name: {}, State: {}, PID: {}\n".format(process_name, state, pid)
        )

        write_state_file(state_dir, process_name, state)
        write_pid_file(pid_dir, process_name, pid)

        # transition from READY to ACKNOWLEDGED
        write_stdout("RESULT 2\nOK")


if __name__ == "__main__":
    main()
