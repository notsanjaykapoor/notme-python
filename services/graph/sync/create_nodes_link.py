import dataclasses

import datadog
import neo4j
import sqlmodel

import env
import log
import models
import services.data_links
import services.graph.query
import services.graph.sync
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


LABEL_LINK = "link"


class CreateNodesLink:
    """
    create graph node(s) from data links

    example: entity with name 'person' will result in graph node with label 'person', and id and name properties
    """

    def __init__(self, db: sqlmodel.Session, neo: neo4j.Session, entity: models.Entity):
        self._db = db
        self._neo = neo
        self._entity = entity

        self._data_link_query = f"src_name:{self._entity.entity_name} src_slug:{self._entity.slug}"
        self._node_label = LABEL_LINK

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

        # create graph node for each data link
        for data_link in struct_data_links.objects:
            node_struct = self._node_merge(data_link)

            struct.nodes_created += node_struct.nodes_created

        return struct

    def _node_id(self, data_link: models.DataLink) -> str:
        return f"{data_link.name_slug_str}:{self._entity.type_value}"

    def _node_merge(self, data_link: models.DataLink) -> NodeCounter:
        node_struct = NodeCounter(0, 0)

        query = f"""
        merge(n:{self._node_label} {{id: $id}}) return n
        """

        params = {"id": self._node_id(data_link)}

        with datadog.statsd.timed("neo.writer", tags=[f"writer:{__name__}"]):
            summary = self._neo.write_transaction(services.graph.tx.write, query, params)

            node_struct.nodes_created += summary.counters.nodes_created

            return node_struct
