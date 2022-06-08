import logging
import typing

from dataclasses import dataclass
from sqlalchemy import exc
from sqlmodel import select, Session

import models


@dataclass
class Struct:
    code: int
    id: typing.Optional[int]
    errors: typing.List[str]


RELATIONSHIP_DEFAULT = "has"


class Create:
    def __init__(self, db: Session, object: dict):
        self._db = db
        self._object = object

        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        self._logger.info(f"{__name__} {self._object}")

        try:
            db_object = models.GraphConnectionEntity(
                entity_name=self._object["entity_name"],
                entity_slug=self._object["entity_slug"],
                rel_name=self._object.get("rel_name", RELATIONSHIP_DEFAULT),
            )
            self._db.add(db_object)
            self._db.commit()

            struct.id = db_object.id
        except exc.IntegrityError:
            self._db.rollback()
            struct.code = 409

        return struct
