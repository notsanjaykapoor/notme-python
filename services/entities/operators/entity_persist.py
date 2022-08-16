import dataclasses

import sqlmodel

import models
import services.entities


@dataclasses.dataclass
class Struct:
    code: int
    ids: list[int]
    entity_ids: set[str]
    location_ids: list[int]
    errors: list[str]


class EntityPersist:
    """
    timely operator to persist entity model
    """

    def __init__(self, db: sqlmodel.Session, entities: list[models.Entity]):
        self._db = db
        self._entities = entities

    def call(self) -> Struct:
        struct = Struct(0, [], set(), [], [])

        # persist to database with version id
        struct_create = services.entities.Create(self._db, entities=self._entities).call()

        if struct_create.code == 0:
            struct.code = 201
            struct.ids += struct_create.ids
            struct.entity_ids = struct_create.entity_ids
            struct.location_ids += struct_create.location_ids

        return struct
