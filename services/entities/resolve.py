import dataclasses

import sqlmodel

import models
import services.entities


@dataclasses.dataclass
class Struct:
    code: int
    entities: list[models.Entity]
    version: int
    fingerprint: str


class Resolve:
    """
    resolve entities by returning:
    - 201 if entities do not exist, indicating this would be a create operation
    - 200 if entities exist without matching fingerprint, indicating this would be an update operation
    - 409 if entities exist with matching fingerprint
    """

    def __init__(self, db: sqlmodel.Session, entities: list[models.Entity]):
        self._db = db
        self._entities = entities

    def call(self) -> Struct:
        struct = Struct(0, [], 0, "")

        struct.fingerprint = services.entities.fingerprint_entities(entities=self._entities)

        struct.entities = self._resolve_matching()

        if not struct.entities:
            # no matches, new entity
            struct.version = 0
            struct.code = 201
            return struct

        # compare fingerprint
        fingerprint_matching = services.entities.fingerprint_entities(entities=struct.entities)

        if fingerprint_matching == struct.fingerprint:
            # matching entities and fingerprint
            struct.code = 409
            return struct

        entity = struct.entities[0]

        # fingerprint is different, entity has changed
        struct.version = entity.version + 1
        struct.fingerprint = services.entities.fingerprint_entities(entities=self._entities)
        struct.code = 200

        return struct

    def _resolve_matching(self) -> list[models.Entity]:
        """return list of matching entities"""
        if not self._entities:
            return []

        struct_list = services.entities.List(
            self._db,
            query=self._resolve_query(),
            offset=0,
            limit=100,
        ).call()

        return struct_list.objects

    def _resolve_query(self) -> str:
        entity_id = self._entities[0].entity_id

        return f"entity_id:{entity_id} state:{models.entity.STATE_ACTIVE}"
