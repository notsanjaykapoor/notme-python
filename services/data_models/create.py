from dataclasses import dataclass

import sqlalchemy
import sqlmodel

import log
import models


@dataclass
class Struct:
    code: int
    object_ids: list[int]
    object_count: int
    errors: list[str]


class Create:
    def __init__(self, db: sqlmodel.Session, objects: list[dict]):
        self._db = db
        self._objects = objects

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        self._logger.info(f"{__name__} {self._objects}")

        try:
            for object in self._objects:
                db_object = models.DataModel(
                    object_name=object["object_name"],
                    object_node=object["object_node"],
                    object_slug=object["object_slug"],
                    object_type=object["object_type"],
                )

                self._db.add(db_object)
                self._db.commit()

                if db_object.id:
                    struct.object_ids.append(db_object.id)
                    struct.object_count += 1
        except sqlalchemy.exc.IntegrityError:
            self._db.rollback()
            struct.code = 409

            self._logger.error(f"{__name__} data model create error")

        return struct
