import logging
from dataclasses import dataclass

import neo4j
import sqlmodel

import models
import services.data_models
import services.entities
import services.graph.sync


@dataclass
class Struct:
    code: int
    relationships_created: int
    errors: list[str]


RELATIONSHIP_NAME = "has"


class CreateRelationshipsHas:
    """
    create graph 'has' relationship from entity object to ll of its properties with node eq 1
    """

    def __init__(self, db: sqlmodel.Session, neo: neo4j.Session, entity: models.Entity):
        self._db = db
        self._neo = neo
        self._entity = entity

        self._entities_query = f"entity_id:{self._entity.entity_id} node:1"
        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        # find all entity properties where node eq 1
        struct_entities = services.entities.List(
            db=self._db,
            query=self._entities_query,
            offset=0,
            limit=1000,
        ).call()

        for entity in struct_entities.objects:
            dst_id = services.entities.graph_value_store(entity.type_name, str(entity.type_value))

            struct.relationships_created += services.graph.sync.CreateRelationship(
                src_id=self._entity.entity_id,
                src_name=self._entity.entity_name,
                dst_id=dst_id,
                dst_name=entity.slug,
                rel_name=RELATIONSHIP_NAME,
                neo=self._neo,
            ).call()

        return struct

    def _entity_matches(self, data_model: models.DataModel) -> list[models.Entity]:
        # find matching entities based on this entity id and matching slug of data model rule
        entity_query = f"entity_id:{self._entity.entity_id} slug:{data_model.object_slug}"

        struct_entities = services.entities.List(
            db=self._db,
            query=entity_query,
            offset=0,
            limit=1000,
        ).call()

        return struct_entities.objects
