import dataclasses

import sqlmodel
import ulid

import models
import services.data_models
import services.entities


@dataclasses.dataclass
class Struct:
    code: int
    entities: list[models.Entity]
    errors: list[str]


class EntityBuild:
    """
    timely operator to build entity model from entity object
    """

    def __init__(self, db: sqlmodel.Session, object: dict):
        self._db = db
        self._object = object

        object_keys = list(self._object.keys())
        self._entity_name, _ = object_keys[0].split(".")
        self._entity_id_key = f"{self._entity_name}._id"

    def call(self) -> Struct:
        struct = Struct(0, [], [])

        try:
            entity_id = self._object[self._entity_id_key]["value"]
            entity_key = f"notme-{entity_id}"

            object_name = self._object_name()
        except Exception:
            struct.code = 422

            return struct

        # cache data_models with node eq 1
        dm_nodes = self._dm_nodes_eq_1()

        for key, value in self._object.items():
            slug = self._object_slug(key)
            node = 0

            # look up node value
            if slug in dm_nodes:
                node = 1

            entity = models.Entity(
                entity_id=entity_id,
                entity_key=entity_key,
                entity_name=self._entity_name,  # e.g. case, person, vehicle
                name=object_name,
                node=node,
                slug=slug,
                state=models.entity.STATE_ACTIVE,
                type_name=value["type"],
                type_value=value["value"],
                version=0,
            )

            struct.entities.append(entity)

        # add entity fingerprint

        fingerprint = services.entities.fingerprint_entities(entities=struct.entities)

        for entity in struct.entities:
            entity.fingerprint = fingerprint

        return struct

    def _dm_nodes_eq_1(self) -> list[str]:
        """get list of data_model slugs with node eq 1"""
        struct_dms = services.data_models.List(
            db=self._db,
            query=f"object_name:{self._entity_name} node:1",
            offset=0,
            limit=1024,
        ).call()

        return [object.object_slug for object in struct_dms.objects]

    def _object_name(self) -> str:
        key = f"{self._entity_name}.name"

        if key in self._object:
            return self._object[key]["value"]

        return self._object_name_default()

    def _object_name_default(self) -> str:
        return f"{self._entity_name} {ulid.new().str}"

    def _object_slug(self, key: str) -> str:
        """parse slug from key, e.g. 'person._id' maps to 'id'"""
        _, slug = key.split(".")

        if slug == "_id":
            return "id"

        return slug
