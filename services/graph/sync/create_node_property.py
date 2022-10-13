import dataclasses

import datadog
import neo4j
import sqlmodel

import log
import models
import services.data_models
import services.entities
import services.graph.query
import services.graph.tx


@dataclasses.dataclass
class NodeCounter:
    code: int
    nodes_created: int


@dataclasses.dataclass
class Struct:
    code: int
    nodes_created: int
    errors: list[str]


ENTITY_SLUG_ID = "id"


class CreateNodeProperty:
    """
    create graph node if entity node value eq 1, with node label 'property' and node id as entity [slug, value]
    """

    def __init__(self, db: sqlmodel.Session, neo: neo4j.Session, entity: models.Entity):
        self._db = db
        self._neo = neo
        self._entity = entity

        self._node_label = models.entity.LABEL_PROPERTY
        self._node_id = f"{self._entity.slug}:{self._entity.type_value}"

        self._logger = log.init("service")

    def _node_count(self, query: str, params: dict) -> int:
        result = services.graph.query.execute(query, params, self._neo)
        return result[0]["count"]

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        # note: slug value 'id' is created separately
        if (self._entity.node == 0) or (self._entity.slug == ENTITY_SLUG_ID):
            return struct

        # create the graph node for this entity
        node_struct = self._node_merge()

        struct.code = node_struct.code
        struct.nodes_created += node_struct.nodes_created

        return struct

    def _node_merge(self) -> NodeCounter:
        node_struct = NodeCounter(0, 0)

        query = f"""
        merge(n:{self._node_label} {{id: $id}}) return n
        """

        params = {"id": self._node_id}

        with datadog.statsd.timed("neo.writer", tags=[f"writer:{__name__}"]):
            summary = self._neo.write_transaction(services.graph.tx.write, query, params)

            node_struct.nodes_created += summary.counters.nodes_created

            return node_struct
