import logging
from dataclasses import dataclass

import neo4j
import sqlmodel

import models
import services.data_links
import services.entities
import services.graph.sync


@dataclass
class Struct:
    code: int
    relationships_created: int
    errors: list[str]


RELATIONSHIP_NAME = "linked"


class CreateRelationshipsLinked:
    """
    create graph 'linked' relationships ...
    """

    def __init__(self, db: sqlmodel.Session, driver: neo4j.Driver, entity: models.Entity):
        self._db = db
        self._driver = driver
        self._entity = entity

        self._data_link_query = f"src_name:{self._entity.entity_name} src_slug:{self._entity.slug}"
        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        # find matching data links
        struct_data_links = services.data_links.List(
            db=self._db,
            query=self._data_link_query,
            offset=0,
            limit=1000,
        ).call()

        if not struct_data_links.objects:
            return struct

        for data_link in struct_data_links.objects:
            entities = self._entity_matches(data_link)

            for entity in entities:
                dst_id = services.entities.graph_value_store(entity.type_name, str(entity.type_value))

                struct.relationships_created += services.graph.sync.CreateRelationship(
                    src_id=self._entity.entity_id,
                    src_name=self._entity.entity_name,
                    dst_id=dst_id,
                    dst_name=entity.slug,
                    rel_name=RELATIONSHIP_NAME,
                    driver=self._driver,
                ).call()

        return struct

    def _entity_matches(self, data_link: models.DataLink) -> list[models.Entity]:
        # find matching entities, filter out self object
        entity_query = self._entity_query(data_link)

        struct_entities = services.entities.List(db=self._db, query=entity_query, offset=0, limit=1000).call()

        matches = [object for object in struct_entities.objects if object.entity_id != self._entity.entity_id]

        return matches

    def _entity_query(self, data_link: models.DataLink) -> str:
        return f"entity_name:{data_link.dst_name} slug:{data_link.dst_slug} type_value:{self._entity.type_value}"
