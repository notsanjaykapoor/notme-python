import os

import datadog

import dot_init  # noqa: F401
import network

CHECK_NAME = "notme.service_check"
CHECK_TAGS = ["check:kafka"]


def service_check() -> int:
    broker = os.environ.get("KAFKA_BROKERS")

    if not broker:
        raise ValueError("kafka brokers not defined")

    host, port = broker.split(":")

    code = network.ping(host, int(port))

    if code == 0:
        status = 0
        message = "ok"
    else:
        status = 2
        message = "kafka down"

    datadog.statsd.service_check(
        check_name=CHECK_NAME,
        status=status,
        message=message,
        tags=CHECK_TAGS,
    )

    datadog.statsd.flush()

    return code
