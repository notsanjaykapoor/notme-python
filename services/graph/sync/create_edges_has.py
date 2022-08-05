import dataclasses

import neo4j
import sqlmodel

import log
import models
import services.data_models
import services.entities
import services.graph.sync


@dataclasses.dataclass
class Struct:
    code: int
    edges_created: int
    edges: list[dict]
    errors: list[str]


DST_LABEL_NAME = "property"
EDGE_NAME = "has"


class CreateEdgesHas:
    """
    create graph 'has' edge from entity object to all of its properties with node eq 1
    """

    def __init__(self, db: sqlmodel.Session, neo: neo4j.Session, entity: models.Entity):
        self._db = db
        self._neo = neo
        self._entity = entity

        self._entities_query = f"entity_id:{self._entity.entity_id} node:1 state:active"
        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [], [])

        # find all entity properties where node eq 1
        struct_entities = services.entities.List(
            db=self._db,
            query=self._entities_query,
            offset=0,
            limit=1000,
        ).call()

        for entity in struct_entities.objects:
            dst_id = str(entity.type_value)

            struct_edge = services.graph.sync.CreateEdge(
                src_id=self._entity.entity_id,
                src_label=self._entity.entity_name,
                dst_id=f"{entity.slug}:{dst_id}",
                dst_label=DST_LABEL_NAME,
                edge_name=EDGE_NAME,
                neo=self._neo,
            ).call()

            struct.edges += struct_edge.edges

        struct.edges_created = len(struct.edges)

        return struct

    def _entity_matches(self, data_model: models.DataModel) -> list[models.Entity]:
        # find matching entities based on this entity id and matching slug of data model rule
        # e.g. "entity_id:123456 slug:jacket_id"
        entity_query = f"entity_id:{self._entity.entity_id} slug:{data_model.object_slug}"

        struct_entities = services.entities.List(
            db=self._db,
            query=entity_query,
            offset=0,
            limit=1000,
        ).call()

        return struct_entities.objects
