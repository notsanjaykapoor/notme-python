import logging
import sys
from dataclasses import dataclass

import sqlalchemy
import sqlmodel

import models
import services.data_models


@dataclass
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

        self._logger.info(f"{__name__} {self._objects}")

        for object in self._objects:
            if (code := self._data_link_validate(object)) > 0:
                struct.code = code
                return struct

            try:
                data_link_objects = self._data_link_objects_swapped(object)

                # map to db objects and add as a single tx
                db_objects = [models.DataLink(**object) for object in data_link_objects]

                for db_object in db_objects:
                    self._db.add(db_object)

                self._db.commit()

                for object in db_objects:
                    assert object.id
                    struct.ids.append(object.id)
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

    def _data_link_objects_swapped(self, object: dict) -> list[dict]:
        """map object to data link objects with src/dst and dst/src"""

        objects = [
            {
                "src_name": object["src_name"],
                "src_slug": object["src_slug"],
                "dst_name": object["dst_name"],
                "dst_slug": object["dst_slug"],
            },
            {
                "src_name": object["dst_name"],
                "src_slug": object["dst_slug"],
                "dst_name": object["src_name"],
                "dst_slug": object["src_slug"],
            },
        ]

        return objects

    def _data_link_validate(self, object: dict) -> int:
        if not all(key in object for key in ("dst_name", "dst_slug", "src_name", "src_slug")):
            return 422

        # slugs must be different
        if object["src_slug"] == object["dst_slug"]:
            return 422

        # data model properties must have object_node eq 1

        code = self._data_link_validate_data_model(
            name=object["src_name"],
            slug=object["src_slug"],
        )

        if code != 0:
            return code

        code = self._data_link_validate_data_model(
            name=object["dst_name"],
            slug=object["dst_slug"],
        )

        if code != 0:
            return code

        return 0

    def _data_link_validate_data_model(self, name: str, slug: str) -> int:
        query = f"object_name:{name} object_slug:{slug} object_node:1"

        struct_list = services.data_models.List(
            db=self._db,
            query=query,
            offset=0,
            limit=1,
        ).call()

        if struct_list.count == 0:
            return 422

        return 0
