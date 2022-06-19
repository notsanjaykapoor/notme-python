import dataclasses
import logging

import sqlalchemy
import sqlmodel

import models


@dataclasses.dataclass
class Struct:
    code: int
    ids: list[int]
    count: int
    errors: list[str]


class Create:
    def __init__(self, db: sqlmodel.Session, objects: list[dict]):
        self._db = db
        self._objects = objects

        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        try:
            for object in self._objects:
                db_object = models.EntityWatch(
                    message=object["message"],
                    output=object.get("output", ""),
                    query=object["query"],
                    topic=object["topic"],
                )
                self._db.add(db_object)
                self._db.commit()

                if db_object.id:
                    struct.ids.append(db_object.id)
                    struct.count += 1
        except sqlalchemy.exc.IntegrityError:
            self._db.rollback()
            struct.code = 409

            self._logger.error(f"{__name__} create error")

        return struct
