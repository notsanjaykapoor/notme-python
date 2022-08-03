import dataclasses

import datadog
import neo4j

import env
import log
import models
import services.graph.query
import services.graph.tx


@dataclasses.dataclass
class Struct:
    code: int
    nodes_created: int
    nodes: list[dict]
    errors: list[str]


@dataclasses.dataclass
class NodeStruct:
    code: int
    node: dict


ENTITY_SLUG_ID = "id"

NODE_LABEL = "entity"


class CreateNodeFromEntityId:
    """
    create graph node from entity object id

    example: entity with name 'person' will map to a graph node labeled 'person:entity', with id and name properties
    """

    def __init__(self, neo: neo4j.Session, entity: models.Entity):
        self._neo = neo
        self._entity = entity

        self._node_id = self._entity.entity_id
        self._node_labels = f"{self._entity.entity_name}:{NODE_LABEL}"
        self._node_name = self._entity.name
        self._version = self._entity.version

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [], [])

        if (self._entity.node == 0) or (self._entity.slug != ENTITY_SLUG_ID):
            return struct

        node_struct = self._node_create()

        struct.code = node_struct.code

        if struct.code not in [0, 409]:
            # error
            return struct

        if struct.code == 0:
            struct.nodes.append(node_struct.node)
            struct.nodes_created += len(struct.nodes)

        return struct

    def _node_count(self, query: str, params: dict) -> int:
        result = services.graph.query.execute(query, params, self._neo)
        return result[0]["count"]

    def _node_create(self) -> NodeStruct:
        node_struct = NodeStruct(
            0,
            {
                "id": self._node_id,
                "label": self._node_labels,
                "name": self._node_name,
            },
        )

        if self._entity.type_value is None:
            # invalid
            node_struct.code = 422
            return node_struct

        query_exists = f"""
        match(n:{self._node_labels} {{id: $id}}) return count(n) as count
        """

        params = {"id": self._node_id, "name": self._node_name}

        node_count = self._node_count(query_exists, params)

        if node_count:
            # node exists
            node_struct.code = 409
            return node_struct

        # note that node label can not be set with '$' format
        query_create = f"create (p:{self._node_labels} {{id: $id, name: $name, version: $version}}) return p"

        params["version"] = str(self._version)

        self._logger.info(f"{__name__} label {self._node_labels} props {params}")

        with datadog.statsd.timed("neo.writer", tags=[f"env:{env.name()}", f"writer:{__name__}"]):
            summary = self._neo.write_transaction(services.graph.tx.write, query_create, params)

            if summary.counters.nodes_created == 0:
                node_struct.code = 500

            return node_struct
