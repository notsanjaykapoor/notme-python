import dataclasses

import datadog
import neo4j

import log
import models
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

LABEL_ENTITY = "entity"


class CreateNodeEntity:
    """
    create graph node from entity object id

    example: entity with name 'person' will map to a graph node labeled 'person:entity', with id and name properties
    """

    def __init__(self, neo: neo4j.Session, entity: models.Entity):
        self._neo = neo
        self._entity = entity

        self._node_id = self._entity.entity_id
        self._node_labels = f"{self._entity.entity_name}:{LABEL_ENTITY}"
        self._node_name = self._entity.name
        self._version = self._entity.version

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        if (self._entity.node == 0) or (self._entity.slug != ENTITY_SLUG_ID):
            return struct

        node_struct = self._node_merge()

        struct.code = node_struct.code
        struct.nodes_created += node_struct.nodes_created

        return struct

    def _node_merge(self) -> NodeCounter:
        node_struct = NodeCounter(0, 0)

        query = f"""
        merge(n:{self._node_labels} {{id: $id}})
        on create set n.name = '{self._node_name}', n.version = {str(self._version)}
        on match set n.name = '{self._node_name}', n.version = {str(self._version)}
        return n
        """

        params = {"id": self._node_id}

        with datadog.statsd.timed("neo.writer", tags=[f"writer:{__name__}"]):
            summary = self._neo.write_transaction(services.graph.tx.write, query, params)

            node_struct.nodes_created += summary.counters.nodes_created

            return node_struct
