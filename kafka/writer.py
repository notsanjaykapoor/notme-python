import dataclasses
import json
import typing

import confluent_kafka

import kafka.config


@dataclasses.dataclass
class Struct:
    code: int
    errors: list[str]


class Writer:
    def __init__(self, topic: str):
        self._topic = topic

        self._producer = confluent_kafka.Producer(kafka.config.config_writer())

    def call(self, key: str, message: typing.Union[dict, str]):
        struct = Struct(0, [])

        if type(message) is dict:
            value_str = json.dumps(message)
        elif type(message) is str:
            value_str = message
        else:
            raise ValueError("invalid message")

        self._producer.produce(self._topic, key=key, value=value_str)
        self._producer.flush()

        return struct
