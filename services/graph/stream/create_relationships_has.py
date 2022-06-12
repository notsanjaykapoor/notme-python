import logging
from dataclasses import dataclass

import neo4j
from sqlmodel import Session

import models
import services.data_nodes
import services.entities
import services.graph
import services.graph.query
import services.graph.stream
import services.graph.tx


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

    def __init__(self, db: Session, driver: neo4j.Driver, entity: models.Entity):
        self._db = db
        self._driver = driver
        self._entity = entity

        self._data_link_query = (
            f"src_name:{self._entity.entity_name} src_slug:{self._entity.slug}"
        )
        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        # find matching data nodes
        struct_data_nodes = services.data_nodes.List(
            db=self._db,
            query=self._data_link_query,
            offset=0,
            limit=1000,
        ).call()

        if not struct_data_nodes.objects:
            return struct

        for data_link in struct_data_nodes.objects:
            entities = self._entity_matches(data_link)

            for entity in entities:
                dst_id = services.entities.graph_value_store(
                    entity.type_name, str(entity.type_value)
                )

                struct.relationships_created += (
                    services.graph.stream.CreateRelationships(
                        src_id=self._entity.entity_id,
                        src_name=self._entity.entity_name,
                        dst_id=dst_id,
                        dst_name=entity.slug,
                        rel_name=RELATIONSHIP_NAME,
                        driver=self._driver,
                    ).call()
                )

        return struct

    def _entity_matches(self, data_link: models.DataLink) -> list[models.Entity]:
        # find matching entities based on this entity id and matching slug of data link rule
        entity_query = f"entity_id:{self._entity.entity_id} slug:{data_link.src_slug}"

        struct_entities = services.entities.List(
            db=self._db, query=entity_query, offset=0, limit=1000
        ).call()

        return struct_entities.objects
