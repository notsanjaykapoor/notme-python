import asyncio
import dataclasses
import json
import logging

import attrs
import datadog
import sqlmodel

import database
import kafka
import models
import services.entities
import services.entities.watches
import services.kafka.topics


@dataclasses.dataclass
class Struct:
    code: int
    errors: list[str]


@attrs.define
class EntityChanges(kafka.Handler):
    _topic: str = services.kafka.topics.TOPIC_ENTITY_CHANGES
    _logger: logging.Logger = logging.getLogger("actor")

    @datadog.statsd.timed(f"{__name__}.timer", tags=["env:dev"])
    async def call(self, msg: models.KafkaMessage) -> kafka.KafkaResult:
        struct = kafka.KafkaResult(0, [])

        task_name = asyncio.current_task().get_name()  # type: ignore

        self._logger.info(f"actor '{task_name}' header {msg.header()}")

        try:
            message_object = json.loads(msg.value())

            self._logger.info(f"actor '{task_name}' try {message_object}")

            if message_object["name"] == "entity.changed":
                with sqlmodel.Session(database.engine) as db:
                    # get entity object
                    entity = services.entities.get_by_id(db=db, id=message_object["id"])

                    if entity:
                        self._entity_match_publish(db, entity)

                self._logger.error(f"actor '{task_name}' processed {message_object}")
            else:
                struct.code = 422
                self._logger.error(f"actor '{task_name}' invalid message {message_object}")
        except Exception as e:
            struct.code = 500

            self._logger.info(f"actor '{task_name}' exception {e}")

        datadog.statsd.increment(f"{__name__}.results.increment", tags=["env:dev", f"code:{struct.code}"])
        datadog.statsd.flush()

        return struct

    def _entity_match_publish(self, db: sqlmodel.Session, entity: models.Entity):
        # find all matching watches
        struct_matches = services.entities.watches.Match(
            db=db,
            entity=entity,
            topic=self._topic,
        ).call()

        for watch in struct_matches.watches:
            if watch.output:
                self._entity_publish(entity=entity, topic=watch.output)

    def _entity_publish(self, entity: models.Entity, topic: str) -> int:
        services.entities.Publish(
            message=entity.message_changed(),
            topic=topic,
        ).call()

        return 0
