import asyncio
import dataclasses
import logging
import typing

import kafka


@dataclasses.dataclass
class Struct:
    code: int
    task: typing.Optional[asyncio.Task]
    errors: list[str]


class Scheduler:
    def __init__(self, topic: str, group: str, handler: kafka.Handler):
        self._topic = topic
        self._group = group
        self._handler = handler

        self._reader = kafka.Reader(self._topic, self._group, self._handler)
        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, None, [])

        self._logger.info(f"{__name__} scheduling task '{self._topic}'")

        struct.task = asyncio.create_task(self._reader.call(), name=self._topic)

        return struct
