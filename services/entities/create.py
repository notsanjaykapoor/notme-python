import dataclasses
import sys

import sqlalchemy
import sqlmodel

import log
import models
import services.entity_locations


@dataclasses.dataclass
class Struct:
    code: int
    ids: list[int]
    count: int
    entity_ids: set[str]
    entity_count: int
    location_count: int
    errors: list[str]


class Create:
    """create entity from list of objects"""

    def __init__(self, db: sqlmodel.Session, objects: list[dict], data_models: dict):
        self._db = db
        self._objects = objects
        self._data_models = data_models

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, set(), 0, 0, [])

        self._logger.info(f"{__name__} {self._objects}")

        try:
            db_objects: list[models.Entity] = [self._entity_object(object) for object in self._objects]

            for db_object in db_objects:
                self._db.add(db_object)

            self._db.commit()

            for db_object in db_objects:
                if db_object.id:
                    struct.ids.append(db_object.id)
                    struct.count += 1
                    struct.entity_ids.add(db_object.entity_id)
                    struct.entity_count = len(struct.entity_ids)

            # create entity locations
            struct_locations = services.entity_locations.Create(db=self._db, entity_ids=list(struct.entity_ids)).call()
            struct.location_count = struct_locations.count
        except sqlalchemy.exc.IntegrityError:
            self._db.rollback()
            struct.code = 409
            self._logger.error(f"{__name__} {sys.exc_info()[0]} error")
        except Exception:
            print(sys.exc_info())  #

            self._db.rollback()
            struct.code = 500
            self._logger.error(f"{__name__} {sys.exc_info()[0]} exception")

        return struct

    def _entity_object(self, object: dict) -> models.Entity:
        # find data model, and use to verify fields
        entity_name = object["entity_name"]
        slug = object["slug"]

        dm_key = f"{entity_name}:{slug}"
        data_model = self._data_models[dm_key]

        node = data_model.object_node  # data model defines node value

        entity_id = object["entity_id"]
        entity_key = object.get("entity_key", f"notme-{entity_id}")

        return models.Entity(
            entity_id=entity_id,
            entity_key=entity_key,
            entity_name=entity_name,
            name=object.get("name", None),
            node=node,
            slug=slug,
            tags=object.get("tags", None),
            type_name=object["type_name"],
            type_value=object["type_value"],
        )
