import logging

from dataclasses import dataclass
from sqlmodel import select, Session
from typing import List, Optional

import models
import services.entities


@dataclass
class Struct:
    code: int
    count: int
    errors: List[str]


class Slurp:
    def __init__(self, db: Session, objects: List[dict]):
        self._db = db
        self._objects = objects

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        for object in self._objects:
            # format object into proper entity objects
            entity_objects = self._object_to_entities(object)

            # persist to database
            struct_create = services.entities.Create(
                self._db, entity_objects=entity_objects
            ).call()

            if struct_create.code == 0:
                struct.count += struct_create.entity_count

        return struct

    def _object_to_entities(self, object: dict) -> List[dict]:
        entities: List[dict] = []

        for properties in object["properties"]:
            entities.append(self._object_to_entity(object, properties))

        return entities

    def _object_to_entity(self, object: dict, properties: dict):
        return {
            "entity_id": object["id"],
            "entity_name": object["model"],
            "slug": properties["slug"],
            "type_name": properties["type"],
            "type_value": properties["value"],
        }
