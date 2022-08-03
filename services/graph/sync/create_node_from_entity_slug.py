import dataclasses

import datadog
import neo4j
import sqlmodel

import env
import log
import models
import services.data_models
import services.entities
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

NODE_LABEL = "property"


class CreateNodeFromEntitySlug:
    """
    create graph node if entity node value eq 1, with node label 'property' and node id as entity [slug, value]
    """

    def __init__(self, db: sqlmodel.Session, neo: neo4j.Session, entity: models.Entity):
        self._db = db
        self._neo = neo
        self._entity = entity

        self._node_label = NODE_LABEL
        self._node_id = f"{self._entity.slug}:{self._entity.type_value}"
        self._version = self._entity.version

        self._logger = log.init("service")

    def _node_count(self, query: str, params: dict) -> int:
        result = services.graph.query.execute(query, params, self._neo)
        return result[0]["count"]

    def call(self) -> Struct:
        struct = Struct(0, 0, [], [])

        # note: slug value 'id' is created separately
        if (self._entity.node == 0) or (self._entity.slug == ENTITY_SLUG_ID):
            return struct

        # create the graph node for this entity
        node_struct = self._node_create()

        struct.code = node_struct.code

        if struct.code not in [0, 409]:
            # error
            return struct

        if struct.code == 0:
            struct.nodes.append(node_struct.node)
            struct.nodes_created += len(struct.nodes)

        return struct

    def _node_create(self) -> NodeStruct:
        node_struct = NodeStruct(
            0,
            {
                "id": self._node_id,
                "label": self._node_label,
            },
        )

        query_exists = f"""
        match(n:{self._node_label} {{id: $id}}) return count(n) as count
        """

        params = {"id": self._node_id}

        if self._node_count(query_exists, params):
            # node exists
            node_struct.code = 409
            return node_struct

        # note that node label can not be set with '$' format
        query_create = f"create (n:{self._node_label} {{id: $id, version: $version}}) RETURN n"

        params["version"] = str(self._version)

        self._logger.info(f"{__name__} label {self._node_label} props {params}")

        with datadog.statsd.timed("neo.writer", tags=[f"env:{env.name()}", f"writer:{__name__}"]):
            summary = self._neo.write_transaction(services.graph.tx.write, query_create, params)

            if summary.counters.nodes_created == 0:
                node_struct.code = 500

            return node_struct
