import dataclasses
import datetime
import logging
import typing

import sqlmodel

import models


@dataclasses.dataclass
class Struct:
    code: int
    name: typing.Optional[str]
    errors: list[str]


class Create:
    def __init__(self, db: sqlmodel.Session, object: dict):
        self._db = db
        self._object = object
        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, None, [])

        self._logger.info(f"{__name__} object {self._object}")

        db_object = models.Event(
            name=self._object.get("name"),
            timestamp=datetime.datetime.utcnow(),
            value=self._object.get("value"),
        )

        self._db.add(db_object)
        self._db.commit()

        struct.name = db_object.name

        return struct
