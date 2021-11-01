#!/usr/bin/python3

import argparse
import logging
import signal
import sys
import time

from flask import Flask
from wsgiref.simple_server import make_server


def _shutdown():
    logging.info("Shutting down, see you next time!")
    sys.exit(1)


def _signal_handler():
    _shutdown()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    @app.route("/")
    def index():
        return "Ok"

    return app


def main():
    signal.signal(signal.SIGTERM, _signal_handler)
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser(description="Integrationtest app")
    parser.add_argument(
        "-p", "--port", default=8080, help="Exposed port", required=False
    )
    args = parser.parse_args()

    app = create_app()

    logging.info("Start exporter, listen on {}".format(int(args.port)))
    httpd = make_server("", int(args.port), app)
    httpd.serve_forever()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
