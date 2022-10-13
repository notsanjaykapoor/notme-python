import dataclasses

import datadog
import neo4j
import neo4j.graph

import env
import log
import models
import services.graph.query
import services.graph.query.types
import services.graph.tx


@dataclasses.dataclass
class Struct:
    code: int
    nodes_deleted: int
    edges_deleted: int
    errors: list[str]


class PruneNodeUnconnected:
    """
    prune nodes with no edges
    """

    def __init__(self, neo: neo4j.Session, entity: models.Entity):
        self._neo = neo
        self._entity = entity

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, 0, [])

        graph_query = self._query_node_delete()

        with datadog.statsd.timed("neo.writer", tags=[f"writer:{__name__}"]):
            summary = self._neo.write_transaction(services.graph.tx.write, graph_query.query, graph_query.params)
            struct.nodes_deleted += summary.counters.nodes_deleted

        return struct

    def _query_node_delete(self) -> services.graph.query.types.GraphQuery:
        struct = services.graph.query.types.GraphQuery("", {})

        struct.query = "match(node) where (node:link or node:property) and (not (node)--()) delete node"
        struct.params = {}

        return struct
