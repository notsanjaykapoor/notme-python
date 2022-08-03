import dataclasses

import models


@dataclasses.dataclass
class Struct:
    code: int
    entities: list[models.Entity]


class Normalize:
    """
    normalize entity objects into entity models
    """

    def __init__(self, object: dict, properties: list[dict], data_models: dict):
        self._object = object
        self._properties = properties
        self._data_models = data_models

    def call(self) -> Struct:
        struct = Struct(0, [])

        for prop_hash in self._properties:
            struct.entities.append(self._normalize_object(prop_hash))

        return struct

    def _normalize_object(self, properties: dict) -> models.Entity:
        # find data model, and use to verify fields
        entity_name = self._object["model"]
        slug = properties["slug"]

        dm_key = f"{entity_name}:{slug}"
        data_model = self._data_models[dm_key]

        node = data_model.object_node  # data model defines node value

        entity_id = self._object["id"]
        entity_key = self._object.get("key", f"notme-{entity_id}")

        return models.Entity(
            entity_id=entity_id,
            entity_key=entity_key,
            entity_name=entity_name,
            name=self._object.get("name", None),
            node=node,
            slug=slug,
            state=models.entity.STATE_ACTIVE,
            tags=self._object.get("tags", None),
            type_name=properties["type"],
            type_value=properties["value"],
        )
