import dataclasses

import datadog
import neo4j
import sqlmodel

import log
import models
import services.graph.query
import services.graph.sync
import services.graph.tx


@dataclasses.dataclass
class NodeStruct:
    code: int
    node: dict


@dataclasses.dataclass
class Struct:
    code: int
    nodes_created: int
    nodes: list[dict]
    errors: list[str]


NODE_LABEL = "link"


class CreateNodesFromDataLinks:
    """
    create graph node(s) from data links

    example: entity with name 'person' will result in graph node with label 'person', and id and name properties
    """

    def __init__(self, db: sqlmodel.Session, neo: neo4j.Session, entity: models.Entity):
        self._db = db
        self._neo = neo
        self._entity = entity

        self._data_link_query = f"src_name:{self._entity.entity_name} src_slug:{self._entity.slug}"
        self._node_label = NODE_LABEL

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [], [])

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
            node_struct = self._node_create(data_link)

            if node_struct.code in [0]:
                struct.nodes.append(node_struct.node)

        struct.nodes_created = len(struct.nodes)

        return struct

    def _node_count(self, query: str, params: dict) -> int:
        result = services.graph.query.execute(query, params, self._neo)
        return result[0]["count"]

    def _node_create(self, data_link: models.DataLink) -> NodeStruct:
        node_struct = NodeStruct(0, {})

        if self._entity.type_value is None:
            node_struct.code = 422
            return node_struct

        node_id = self._node_id(data_link)

        query_exists = f"""
        match(n:{self._node_label} {{id: $id}}) return count(n) as count
        """

        params = {"id": node_id}

        node_count = self._node_count(query_exists, params)

        node_struct.node = {
            "id": node_id,
            "label": self._node_label,
        }

        if node_count:
            # node exists
            node_struct.code = 409
            return node_struct

        # note that node label can not be set with '$' format
        query_create = f"create (p:{self._node_label} {{id: $id}}) return p"

        self._logger.info(f"{__name__} label {self._node_label} props {params}")

        with datadog.statsd.timed(f"{__name__}.timer", tags=["env:dev", "neo:write"]):
            summary = self._neo.write_transaction(services.graph.tx.write, query_create, params)

            if summary.counters.nodes_created == 0:
                node_struct.code = 500

            return node_struct

    def _node_id(self, data_link: models.DataLink) -> str:
        return f"{data_link.name_slug_str}:{self._entity.type_value}"
