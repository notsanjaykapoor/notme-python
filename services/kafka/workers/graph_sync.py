import asyncio
import dataclasses
import json
import logging
import typing

import attrs
import sqlmodel

import database
import kafka
import models
import services.entities
import services.graph.driver
import services.graph.stream
import services.kafka.topics


@dataclasses.dataclass
class Struct:
    code: int
    task: typing.Optional[asyncio.Task]
    errors: list[str]


@attrs.define
class GraphSync(kafka.Handler):
    _topic: str = services.kafka.topics.TOPIC_GRAPH_SYNC
    _logger: logging.Logger = logging.getLogger("actor")

    async def call(self, msg: models.KafkaMessage) -> kafka.KafkaResult:
        struct = kafka.KafkaResult(0, [])

        task_name = asyncio.current_task().get_name()  # type: ignore

        self._logger.info(f"actor '{task_name}' message header {msg.header()}")

        try:
            message_object = json.loads(msg.value())

            self._logger.info(f"actor '{task_name}' message body {message_object}")

            if message_object["name"] == "entity.changed":
                with sqlmodel.Session(database.engine) as db:
                    # get entity object
                    entity = services.entities.get_by_id(db=db, id=message_object["id"])

                    if not entity:
                        return struct

                    with services.graph.driver.get() as driver:
                        # process message
                        services.graph.stream.Process(db=db, driver=driver, entity=entity).call()

        except Exception as e:
            struct.code = 500

            self._logger.error(f"actor '{task_name}' exception {e}")

        return struct
