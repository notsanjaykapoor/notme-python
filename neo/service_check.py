import os

import datadog

import doginit  # noqa: F401
import dotinit  # noqa: F401
import network

CHECK_NAME = "notme.service_check"
CHECK_TAGS = ["check:neo"]


def service_check() -> int:
    neo_url = os.environ.get("NEO4J_BOLT_URL")

    if not neo_url:
        raise ValueError("neo4j url not defined")

    _, host, port = neo_url.split(":")
    host = host.replace("/", "")

    code = network.ping(host, int(port))

    if code == 0:
        status = 0
        message = "ok"
    else:
        status = 2
        message = "neo4j down"

    datadog.statsd.service_check(
        check_name=CHECK_NAME,
        status=status,
        message=message,
        tags=CHECK_TAGS,
    )

    datadog.statsd.flush()

    return code
