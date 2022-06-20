import asyncio
import dataclasses
import json
import logging
import typing

import attrs
import datadog
import sqlmodel

import database
import kafka
import models
import services.entities
import services.entities.watches
import services.graph.driver
import services.graph.sync
import services.kafka.topics


@dataclasses.dataclass
class Struct:
    code: int
    task: typing.Optional[asyncio.Task]
    errors: list[str]


@attrs.define
class GraphHandler(kafka.Handler):
    _topic: str = services.kafka.topics.TOPIC_GRAPH_SYNC
    _logger: logging.Logger = logging.getLogger("actor")

    @datadog.statsd.timed(f"{__name__}.timer", tags=["env:dev", "neo:service", "queue:reader"])
    async def call(self, msg: models.KafkaMessage) -> kafka.KafkaResult:
        struct = kafka.KafkaResult(0, [])

        task_name = asyncio.current_task().get_name()  # type: ignore

        self._logger.info(f"actor '{task_name}' header {msg.header()}")

        try:
            message_object = json.loads(msg.value())

            self._logger.info(f"actor '{task_name}' try {message_object}")

            if message_object["name"] == "entity.changed":
                with sqlmodel.Session(database.engine) as db:
                    with services.graph.driver.get() as driver:
                        # process message
                        services.graph.sync.Entity(db=db, driver=driver, entity_id=message_object["id"]).call()

                self._logger.info(f"actor '{task_name}' processed {message_object}")
            elif message_object["name"] == "entity.geo.changed":
                with sqlmodel.Session(database.engine) as db:
                    with services.graph.driver.get() as driver:
                        # process message
                        services.graph.sync.EntityGeo(db=db, driver=driver, entity_id=message_object["id"]).call()

                        # check watches
                        struct_watches = services.entities.watches.Match(
                            db=db,
                            entity_ids=[message_object["id"]],
                            topic=self._topic,
                        ).call()

                        # publish entity messages
                        services.entities.watches.Publish(
                            watches=struct_watches.watches,
                            entity_ids=[message_object["id"]],
                        ).call()

                self._logger.info(f"actor '{task_name}' processed {message_object}")
            else:
                struct.code = 422
                self._logger.error(f"actor '{task_name}' invalid message {message_object}")
        except Exception as e:
            struct.code = 500

            self._logger.error(f"actor '{task_name}' exception {e}")

        datadog.statsd.increment(f"{__name__}.results.increment", tags=["env:dev", f"code:{struct.code}"])
        datadog.statsd.flush()

        return struct
