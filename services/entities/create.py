import dataclasses
import logging
import sys

import sqlalchemy
import sqlmodel

import models


@dataclasses.dataclass
class Struct:
    code: int
    ids: list[int]
    entity_ids: set[str]
    count: int
    errors: list[str]


class Create:
    """create entity from list of objects"""

    def __init__(self, db: sqlmodel.Session, objects: list[dict]):
        self._db = db
        self._objects = objects

        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, [], set(), 0, [])

        self._logger.info(f"{__name__} {self._objects}")

        try:
            db_objects: list[models.Entity] = [self._entity_object(object) for object in self._objects]

            for db_object in db_objects:
                self._db.add(db_object)

            self._db.commit()

            for db_object in db_objects:
                if db_object.id:
                    struct.ids.append(db_object.id)
                    struct.entity_ids.add(db_object.entity_id)
                    struct.count += 1

        except sqlalchemy.exc.IntegrityError:
            self._db.rollback()
            struct.code = 409
            self._logger.error(f"{__name__} {sys.exc_info()[0]} error")
        except Exception:
            self._db.rollback()
            struct.code = 500
            self._logger.error(f"{__name__} {sys.exc_info()[0]} exception")

        return struct

    def _entity_object(self, object: dict) -> models.Entity:
        return models.Entity(
            entity_id=object["entity_id"],
            entity_key=object.get("entity_key", ""),
            entity_name=object["entity_name"],
            name=object.get("name", None),
            slug=object["slug"],
            tags=object.get("tags", None),
            type_name=object["type_name"],
            type_value=object["type_value"],
        )
