import os
import socket

config_reader = {
    "auto.offset.reset": "smallest",
    "bootstrap.servers": os.environ.get("KAFKA_BROKERS"),
    "client.id": socket.gethostname(),
    "enable.auto.commit": False,
}

config_writer = {
    "bootstrap.servers": os.environ.get("KAFKA_BROKERS"),
    "client.id": socket.gethostname(),
}
