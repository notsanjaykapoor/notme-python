import os
import socket


def config_reader(group_id: str) -> dict:
    return {
        "auto.offset.reset": "smallest",
        "bootstrap.servers": os.environ.get("KAFKA_BROKERS"),
        "client.id": socket.gethostname(),
        "enable.auto.commit": False,
        "group.id": group_id,
    }


def config_writer() -> dict:
    return {
        "bootstrap.servers": os.environ.get("KAFKA_BROKERS"),
        "client.id": socket.gethostname(),
    }
