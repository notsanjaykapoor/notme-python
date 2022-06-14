from dataclasses import dataclass

import sqlmodel

import services.entities


@dataclass
class Struct:
    code: int
    count: int
    errors: list[str]


class Slurp:
    def __init__(self, db: sqlmodel.Session, objects: list[dict]):
        self._db = db
        self._objects = objects

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        for object in self._objects:
            # format object into proper entity objects
            entity_objects = self._object_to_entities(object)

            # check if entity(s) exist
            if self._get_entities_count(entity_objects) == 0:
                continue

            # persist to database
            struct_create = services.entities.Create(self._db, entity_objects=entity_objects).call()

            if struct_create.code == 0:
                struct.count += struct_create.count

        return struct

    def _get_entities_count(self, entity_objects: list[dict]) -> int:
        if not entity_objects:
            return 0

        entity_id = entity_objects[0]["entity_id"]

        struct_list = services.entities.List(self._db, query=f"entity_id:{entity_id}", offset=0, limit=100).call()

        return struct_list.count

    def _object_to_entities(self, object: dict) -> list[dict]:
        entities: list[dict] = []

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
