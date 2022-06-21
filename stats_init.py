import os

import datadog

options = {
    "statsd_host": os.environ.get("DATADOG_STATSD_HOST"),
    "statsd_port": os.environ.get("DATADOG_STATSD_PORT"),
}


datadog.initialize(**options)
