import dataclasses
import json

import sqlmodel
import ulid

import services.data_models
import services.entities
import services.kafka.topics


@dataclasses.dataclass
class Struct:
    code: int
    ids: list[int]
    entity_ids: set[str]
    count: int
    errors: list[str]


class Slurp:
    def __init__(self, db: sqlmodel.Session, json_file: str):
        self._db = db
        self._json_file = json_file

        self._objects = json.load(open(self._json_file))

    def call(self) -> Struct:
        struct = Struct(0, [], set(), 0, [])

        struct_dms = services.data_models.Hash(db=self._db, query="").call()

        for object in self._objects:
            object = self._object_props_validate_id_present(object)

            properties = self._object_props_validate_id_slug_present(
                object=object,
                properties=object["properties"],
            )

            if self._object_props_validate_id(object, properties) != 0:
                struct.code = 422
                struct.errors.append("invalid id")
                return struct

            # format object into proper entity objects
            entity_objects = self._object_to_entities(object, properties)

            # check if entity(s) exist
            if self._entities_matching_count(entity_objects) > 0:
                continue

            # persist to database
            struct_create = services.entities.Create(
                self._db,
                objects=entity_objects,
                data_models=struct_dms.object,
            ).call()

            if struct_create.code == 0:
                struct.count += struct_create.count
                struct.ids += struct_create.ids
                struct.entity_ids |= struct_create.entity_ids

        return struct

    def _entities_matching_count(self, entity_objects: list[dict]) -> int:
        """return count of matching entities"""
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

    def _object_props_validate_id(self, object: dict, properties: list[dict]) -> int:
        """validate object id matches id slug"""
        prop_hash = [prop_hash for prop_hash in properties if prop_hash["slug"] == "id"][0]

        if prop_hash["value"] != object["id"]:
            # invalid id
            return 1

        return 0

    def _object_props_validate_id_present(self, object: dict) -> dict:
        """add object id iff its missing"""

        if "id" in object:
            return object

        # clone and add id property
        object_clone = object.copy()

        object_clone["id"] = ulid.new().str

        return object_clone

    def _object_props_validate_id_slug_present(self, object: dict, properties: list[dict]) -> list[dict]:
        """add id slug iff its missing"""
        slugs = [property["slug"] for property in properties]

        if "id" in slugs:
            return properties

        # clone and add id property
        props_clone = properties.copy()

        props_clone.append(
            {
                "slug": "id",
                "type": "string",
                "value": object["id"],
            }
        )

        return props_clone

    def _object_to_entities(self, object: dict, properties: list[dict]) -> list[dict]:
        entities: list[dict] = []

        for prop_hash in properties:
            entities.append(self._object_to_entity(object, prop_hash))

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
