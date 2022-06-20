import os

import datadog

import dotinit  # noqa: F401

options = {
    "statsd_host": os.environ.get("DATADOG_STATSD_HOST"),
    "statsd_port": os.environ.get("DATADOG_STATSD_PORT"),
}


def init():
    datadog.initialize(**options)
