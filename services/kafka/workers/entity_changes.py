import asyncio
import dataclasses
import json
import logging
import typing

import kafka
import models


@dataclasses.dataclass
class Struct:
    code: int
    task: typing.Optional[asyncio.Task]
    errors: list[str]


class EntityChanges(kafka.Handler):
    def __init__(self):
        self._logger = logging.getLogger("actor")
        self._task = None

    async def call(self, msg: models.KafkaMessage) -> kafka.KafkaResult:
        struct = kafka.KafkaResult(0, [])

        self._logger.info(f"actor '{self._task_name()}' message header {msg.header()}")

        try:
            message_object = json.loads(msg.value())

            self._logger.info(f"actor '{self._task_name()}' message body {message_object}")
        except Exception as e:
            struct.code = 500

            self._logger.error(f"actor '{self._task_name()}' exception {e}")

        return struct

    def _task_name(self) -> str:
        self._task = self._task or asyncio.current_task()
        return self._task.get_name()  # type: ignore
