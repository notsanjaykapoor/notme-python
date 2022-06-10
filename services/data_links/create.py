import logging

from dataclasses import dataclass
from sqlalchemy import exc
from sqlmodel import Session

import models


@dataclass
class Struct:
    code: int
    object_ids: list[int]
    object_count: int
    errors: list[str]


class Create:
    def __init__(self, db: Session, objects: list[dict]):
        self._db = db
        self._objects = objects

        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        self._logger.info(f"{__name__} {self._objects}")

        try:
            for object in self._objects:
                db_object = models.DataLink(
                    src_name=object["src_name"],
                    src_slug=object["src_slug"],
                    dst_name=object["dst_name"],
                    dst_slug=object["dst_slug"],
                )

                self._db.add(db_object)
                self._db.commit()

                if db_object.id:
                    struct.object_ids.append(db_object.id)
                    struct.object_count += 1
        except exc.IntegrityError:
            self._db.rollback()
            struct.code = 409

            self._logger.error(f"{__name__} data link create error")

        return struct
