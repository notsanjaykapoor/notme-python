import logging
import typing

from dataclasses import dataclass
from sqlalchemy import exc
from sqlmodel import select, Session

import models


@dataclass
class Struct:
    code: int
    object_ids: typing.List[int]
    object_count: int
    errors: typing.List[str]


class Create:
    def __init__(self, db: Session, objects: typing.List[dict]):
        self._db = db
        self._objects = objects

        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        self._logger.info(f"{__name__} {self._objects}")

        try:
            for object in self._objects:
                db_object = models.DataModel(
                    object_name=object["object_name"],
                    object_slug=object["object_slug"],
                    object_type=object["object_type"],
                )

                self._db.add(db_object)
                self._db.commit()

                if db_object.id:
                    struct.object_ids.append(db_object.id)
                    struct.object_count += 1
        except exc.IntegrityError:
            self._db.rollback()
            struct.code = 409

            self._logger.error(f"{__name__} data model create error")

        return struct
