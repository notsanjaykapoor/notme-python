import asyncio
import dataclasses
import json
import logging
import typing

import attrs

import kafka
import log
import models
import services.entities
import services.graph.session
import services.graph.sync
import services.kafka.topics


@dataclasses.dataclass
class Struct:
    code: int
    task: typing.Optional[asyncio.Task]
    errors: list[str]


@attrs.define
class GeofenceHandler(kafka.Handler):
    _topic: str = services.kafka.topics.TOPIC_GEOFENCE_ALERTS
    _logger: logging.Logger = log.init("actor")

    async def call(self, msg: models.KafkaMessage) -> kafka.KafkaResult:
        struct = kafka.KafkaResult(0, [])

        task_name = asyncio.current_task().get_name()  # type: ignore

        self._logger.info(f"actor '{task_name}' header {msg.header()}")

        try:
            message_object = json.loads(msg.value())

            self._logger.info(f"actor '{task_name}' try {message_object}")

            if message_object["name"] == "geofence.entered":
                self._logger.info(f"actor '{task_name}' processed {message_object}")

        except Exception as e:
            struct.code = 500

            self._logger.error(f"actor '{task_name}' exception {e}")

        return struct
