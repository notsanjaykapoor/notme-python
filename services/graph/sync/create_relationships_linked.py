import dataclasses

import neo4j
import sqlmodel

import log
import models
import services.data_links
import services.entities
import services.graph.sync


@dataclasses.dataclass
class Struct:
    code: int
    relationships_created: int
    errors: list[str]


RELATIONSHIP_NAME = "linked"


class CreateRelationshipsLinked:
    """
    create graph 'linked' relationships based on the following rules:

    - find data_links that match entity name and slug, as source node
    - for each source node, create relationship to target nodes with matching dst_name and dst_slug
    """

    def __init__(self, db: sqlmodel.Session, neo: neo4j.Session, entity: models.Entity):
        self._db = db
        self._neo = neo
        self._entity = entity

        self._data_link_query = f"src_name:{self._entity.entity_name} src_slug:{self._entity.slug}"
        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        if self._entity.node == 0:
            return struct

        # find matching data links
        struct_data_links = services.data_links.List(
            db=self._db,
            query=self._data_link_query,
            offset=0,
            limit=1024,
        ).call()

        if not struct_data_links.objects:
            return struct

        for data_link in struct_data_links.objects:
            # create symmetric relationships between src and dst

            struct.relationships_created += services.graph.sync.CreateEdge(
                src_id=str(self._entity.type_value),
                src_label=self._entity.slug,
                dst_id=str(self._entity.type_value),
                dst_label=data_link.dst_slug,
                edge_name=RELATIONSHIP_NAME,
                neo=self._neo,
            ).call()

            struct.relationships_created += services.graph.sync.CreateEdge(
                src_id=str(self._entity.type_value),
                src_label=data_link.dst_slug,
                dst_id=str(self._entity.type_value),
                dst_label=self._entity.slug,
                edge_name=RELATIONSHIP_NAME,
                neo=self._neo,
            ).call()

        return struct

    def _entity_matches(self, data_link: models.DataLink) -> list[models.Entity]:
        entity_query = self._entity_query(data_link)

        struct_entities = services.entities.List(db=self._db, query=entity_query, offset=0, limit=1000).call()

        matches = [object for object in struct_entities.objects if object.entity_id != self._entity.entity_id]

        return matches

    def _entity_query(self, data_link: models.DataLink) -> str:
        return f"entity_name:{data_link.dst_name} slug:{data_link.dst_slug} type_value:{self._entity.type_value}"
