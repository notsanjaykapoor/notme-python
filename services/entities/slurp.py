import dataclasses
import json

import sqlmodel

import services.entities
import services.kafka.topics


@dataclasses.dataclass
class Struct:
    code: int
    ids: list[int]
    count: int
    errors: list[str]


class Slurp:
    def __init__(self, db: sqlmodel.Session, json_file: str):
        self._db = db
        self._json_file = json_file

        self._objects = json.load(open(self._json_file))

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        for object in self._objects:
            # format object into proper entity objects
            entity_objects = self._object_to_entities(object)

            # check if entity(s) exist
            if self._get_entities_count(entity_objects) > 0:
                continue

            # persist to database
            struct_create = services.entities.Create(self._db, objects=entity_objects).call()

            if struct_create.code == 0:
                struct.count += struct_create.count
                struct.ids += struct_create.ids

        return struct

    def _get_entities_count(self, entity_objects: list[dict]) -> int:
        if not entity_objects:
            return 0

        entity_id = entity_objects[0]["entity_id"]

        struct_list = services.entities.List(
            self._db,
            query=f"entity_id:{entity_id}",
            offset=0,
            limit=100,
        ).call()

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
            "name": object["name"],
            "slug": properties["slug"],
            "tags": object.get("tags", None),
            "type_name": properties["type"],
            "type_value": properties["value"],
        }

    # def _message_publish(self, entity_ids: list[int]):
    #     for entity_id in entity_ids:
    #         message = models.Entity.message_changed_cls(int(entity_id))

    #         services.entities.Publish(
    #             message=message,
    #             topic=services.kafka.topics.TOPIC_ENTITY_CHANGES,
    #         ).call()
