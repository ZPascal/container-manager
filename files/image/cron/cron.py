#!/usr/bin/python3

from crontab import CronTab
import argparse
import logging
import time
import subprocess
import sys
import signal
import os


def _parse_crontab(crontab_file: str) -> list:
    logger = logging.getLogger("parser")

    logger.info(f"Reading crontab from {crontab_file}")

    if not os.path.isfile(crontab_file):
        logger.error(f"Crontab {crontab_file} does not exist. Exiting!")
        sys.exit(1)

    crontab = open(crontab_file, "r")
    lines: list = crontab.readlines()
    crontab.close()

    logger.info(f"{len(lines)} lines read from crontab {crontab_file}")

    jobs: list = list()

    for i, line in enumerate(lines):
        line: str = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        logger.info(f"Parsing line {line}")

        expression: list = line.split(" ", 5)
        cron_expression: str = " ".join(expression[0:5])

        logger.info(f"Cron expression is {cron_expression}")

        try:
            cron_entry = CronTab(cron_expression)
        except ValueError as e:
            logger.critical(
                f"Unable to parse crontab. Line {i + 1}: Illegal cron expression {cron_expression}. Error message: {e}"
            )
            sys.exit(1)

        command: str = expression[5]

        logger.info(f"Command is {command}")

        jobs.append([cron_entry, command])

    if len(jobs) == 0:
        logger.error(
            "Specified crontab does not contain any scheduled execution. Exiting!"
        )
        sys.exit(1)

    return jobs


def _get_next_executions(jobs: list):
    logger = logging.getLogger("next-exec")

    scheduled_executions: tuple = tuple(
        (x[1], int(x[0].next(default_utc=True)) + 1) for x in jobs
    )

    logger.debug(f"Next executions of scheduled are {scheduled_executions}")

    next_exec_time: int = int(min(scheduled_executions, key=lambda x: x[1])[1])

    logger.debug(f"Next execution is in {next_exec_time} second(s)")

    next_commands: list = [x[0] for x in scheduled_executions if x[1] == next_exec_time]

    logger.debug(
        f"Next commands to be executed  in {next_exec_time} are {next_commands}"
    )

    return next_exec_time, next_commands


def _loop(jobs: list):
    logger = logging.getLogger("loop")

    logger.info("Entering main loop")

    while True:
        sleep_time, commands = _get_next_executions(jobs)

        logger.debug(f"Sleeping for {sleep_time} second(s)")

        if sleep_time <= 1:
            logger.debug("Sleep time <= 1 second, ignoring.")
            time.sleep(1)
            continue

        time.sleep(sleep_time)

        for command in commands:
            _execute_command(command)


def _execute_command(command: str):
    logger = logging.getLogger("exec")

    logger.info(f"Executing command {command}")

    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    logger.info(f"Standard output: {result.stdout}")
    logger.info(f"Standard error: {result.stderr}")


def _signal_handler():
    logger = logging.getLogger("signal")
    logger.info("Exiting")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    parser = argparse.ArgumentParser(description="cron")
    parser.add_argument("-c", "--crontab", required=True, type=str)
    logging_target = parser.add_mutually_exclusive_group(required=True)
    logging_target.add_argument("-L", "--logfile", type=str)
    logging_target.add_argument("-C", "--console", action="store_true")
    parser.add_argument(
        "-l",
        "--loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        type=str,
    )

    args = parser.parse_args()

    log_level = getattr(logging, args.loglevel.upper(), logging.INFO)

    if args.console:
        logging.basicConfig(
            filemode="w",
            level=log_level,
            format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        )
    else:
        logging.basicConfig(
            filename=args.logfile,
            filemode="a+",
            level=log_level,
            format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        )

    logger = logging.getLogger("main")

    logger.info("Starting cron")

    jobs: list = _parse_crontab(args.crontab)

    _loop(jobs)


if __name__ == "__main__":
    main()