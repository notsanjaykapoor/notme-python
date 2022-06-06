import json
import logging

from dataclasses import dataclass
from typing import Any

from confluent_kafka import Producer
from kafka.config import config_writer


@dataclass
class Struct:
    code: int
    errors: list[str]


class Writer:
    def __init__(self, topic: str):
        self._topic = topic

        self._producer = Producer(config_writer)
        self._logger = logging.getLogger("service")

    def call(self, key: str, message: Any):
        struct = Struct(0, [])

        if type(message) is dict:
            value_str = json.dumps(message)
        elif type(message) is str:
            value_str = message
        else:
            raise ValueError("invalid message")

        self._logger.info(f"{__name__} topic {self._topic} message {value_str}")

        self._producer.produce(self._topic, key=key, value=value_str)
        self._producer.flush()

        return struct
