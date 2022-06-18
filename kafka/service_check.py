import os

import datadog
import dotenv

import dog
import kafka

dotenv.load_dotenv()

# initialize datadog
dog.init()

CHECK_NAME = "notme.kafka"


def service_check() -> int:
    broker = os.environ.get("KAFKA_BROKERS")

    if not broker:
        raise ValueError("kafka brokers not defined")

    host, port = broker.split(":")

    code = kafka.ping(host, int(port))

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
    )

    datadog.statsd.flush()

    return code
