#!/usr/bin/python3

from crontab import CronTab
import argparse
import logging
import time
import subprocess
import sys
import signal
import os


def parse_crontab(crontab_file):
    logger = logging.getLogger("parser")

    logger.info("Reading crontab from %s", crontab_file)

    if not os.path.isfile(crontab_file):
        logger.error("Crontab %s does not exist. Exiting!", crontab_file)
        sys.exit(1)

    crontab = open(crontab_file, "r")

    lines = crontab.readlines()

    crontab.close()

    logger.info("%s lines read from crontab %s", len(lines), crontab_file)

    jobs = []

    for i, line in enumerate(lines):
        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        logger.info("Parsing line %s", line)

        expression = line.split(" ", 5)
        cron_expression = " ".join(expression[0:5])

        logger.info("Cron expression is %s", cron_expression)

        try:
            cron_entry = CronTab(cron_expression)
        except ValueError as e:
            logger.critical(
                "Unable to parse crontab. Line %s: Illegal cron expression %s. Error message: %s",
                i + 1,
                cron_expression,
                e,
            )
            sys.exit(1)

        command = expression[5]

        logger.info("Command is %s", command)

        jobs.append([cron_entry, command])

    if len(jobs) == 0:
        logger.error(
            "Specified crontab does not contain any scheduled execution. Exiting!"
        )
        sys.exit(1)

    return jobs


def get_next_executions(jobs):
    logger = logging.getLogger("next-exec")

    scheduled_executions = tuple(
        (x[1], int(x[0].next(default_utc=True)) + 1) for x in jobs
    )

    logger.debug(f"Next executions of scheduled are {scheduled_executions}")

    next_exec_time = min(scheduled_executions, key=lambda x: x[1])[1]

    logger.debug(f"Next execution is in {next_exec_time} second(s)")

    next_commands = [x[0] for x in scheduled_executions if x[1] == next_exec_time]

    logger.debug(
        f"Next commands to be executed  in {next_exec_time} are {next_commands}"
    )

    return next_exec_time, next_commands


def loop(jobs):
    logger = logging.getLogger("loop")

    logger.info("Entering main loop")

    while True:
        next_exec_time, commands = get_next_executions(jobs)
        sleep_time = int(next_exec_time)

        logger.debug(f"Sleeping for {sleep_time} second(s)")

        if sleep_time <= 1:
            logger.debug("Sleep time <= 1 second, ignoring.")
            time.sleep(1)
            continue

        time.sleep(sleep_time)

        for command in commands:
            execute_command(command)


def execute_command(command):
    logger = logging.getLogger("exec")

    logger.info("Executing command %s", command)

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    output = process.communicate()
    logger.info(f"Standard output: {output[0]}")
    logger.info(f"Standard error: {output[1]}")


def signal_handler():
    logger = logging.getLogger("signal")
    logger.info("Exiting")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = argparse.ArgumentParser(description="cron")
    parser.add_argument("-c", "--crontab", required=True)
    logging_target = parser.add_mutually_exclusive_group(required=True)
    logging_target.add_argument("-L", "--logfile")
    logging_target.add_argument("-C", "--console", action="store_true")
    parser.add_argument(
        "-l",
        "--loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
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

    jobs = parse_crontab(args.crontab)

    loop(jobs)


main()
