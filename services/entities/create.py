import logging
import typing

from dataclasses import dataclass
from sqlalchemy import exc
from sqlmodel import select, Session

import models


@dataclass
class Struct:
    code: int
    entity_ids: typing.List[str]
    entity_count: int
    errors: typing.List[str]


class Create:
    def __init__(self, db: Session, entity_objects: typing.List[dict]):
        self._db = db
        self._entity_objects = entity_objects
        self._logger = logging.getLogger("api")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        self._logger.info(f"{__name__} {self._entity_objects}")

        try:
            for entity_object in self._entity_objects:
                db_object = models.Entity(
                    entity_id=entity_object["entity_id"],
                    entity_name=entity_object["entity_name"],
                    slug=entity_object["slug"],
                    type_name=entity_object["type_name"],
                    type_value=entity_object["type_value"],
                )
                self._db.add(db_object)

                struct.entity_ids.append(db_object.entity_id)
                struct.entity_count += 1

            # commit all entities as a single transaction
            self._db.commit()
        except exc.IntegrityError:
            self._db.rollback()
            struct.entity_ids = []
            struct.entity_count = 0
            struct.code = 409

            self._logger.error(f"{__name__} entity create error")

        return struct
