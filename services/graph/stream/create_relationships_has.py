import logging
from dataclasses import dataclass

import neo4j
import sqlmodel

import models
import services.data_models
import services.entities
import services.graph.stream


@dataclass
class Struct:
    code: int
    relationships_created: int
    errors: list[str]


RELATIONSHIP_NAME = "has"


class CreateRelationshipsHas:
    """
    create graph 'has' relationship from entity object to 0 or more of its properties, based on data node rules:
      -
    """

    def __init__(self, db: sqlmodel.Session, driver: neo4j.Driver, entity: models.Entity):
        self._db = db
        self._driver = driver
        self._entity = entity

        self._data_model_query = f"object_name:{self._entity.entity_name} object_slug:{self._entity.slug} object_node:1"
        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        # find matching data models with object_node eq 1
        struct_data_models = services.data_models.List(
            db=self._db,
            query=self._data_model_query,
            offset=0,
            limit=1000,
        ).call()

        for data_model in struct_data_models.objects:
            # find entities that match this data model
            entities = self._entity_matches(data_model)

            for entity in entities:
                dst_id = services.entities.graph_value_store(entity.type_name, str(entity.type_value))

                struct.relationships_created += services.graph.stream.CreateRelationship(
                    src_id=self._entity.entity_id,
                    src_name=self._entity.entity_name,
                    dst_id=dst_id,
                    dst_name=entity.slug,
                    rel_name=RELATIONSHIP_NAME,
                    driver=self._driver,
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
