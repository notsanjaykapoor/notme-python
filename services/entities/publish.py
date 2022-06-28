import dataclasses
import typing

import ulid

import kafka


@dataclasses.dataclass
class Struct:
    code: int
    errors: list[str]


class Publish:
    def __init__(self, message: dict, topic: str, key: typing.Optional[str] = None):
        self._message = message
        self._topic = topic

        self._key = key or ulid.new().str

    def call(self) -> Struct:
        struct = Struct(0, [])

        writer = kafka.Writer(topic=self._topic)

        # write message to kafka stream
        writer.call(
            key=ulid.new().str,
            message=self._message,
        )

        return struct
