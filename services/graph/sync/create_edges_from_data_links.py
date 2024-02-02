import dataclasses

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
    edges_created: int
    edges: list[dict]
    errors: list[str]


EDGE_NAME = "linked"
NODE_LABEL = "link"


class CreateEdgesFromDataLinks:
    """
    create graph edge(s) from data links

    example: entity with name 'person' will result in graph node with label 'person', and id and name properties
    """

    def __init__(self, db: sqlmodel.Session, neo: neo4j.Session, entity: models.Entity):
        self._db = db
        self._neo = neo
        self._entity = entity

        self._data_link_query = f"src_name:{self._entity.entity_name} src_slug:{self._entity.slug}"
        self._node_label = NODE_LABEL
        self._edge_name = EDGE_NAME

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
            struct.edges += self._edges_create(data_link)

        struct.edges_created = len(struct.edges)

        return struct

    def _edges_create(self, data_link: models.DataLink) -> list[dict]:
        edges: list[dict] = []

        if self._entity.type_value is None:
            return edges

        node_id = self._node_id(data_link)

        struct_edge = services.graph.sync.CreateEdge(
            src_id=self._entity.entity_id,
            src_label=self._entity.entity_name,
            dst_id=node_id,
            dst_label=self._node_label,
            edge_name=self._edge_name,
            neo=self._neo,
        ).call()

        edges += struct_edge.edges

        # create reverse edge

        struct_edge = services.graph.sync.CreateEdge(
            src_id=node_id,
            src_label=self._node_label,
            dst_id=self._entity.entity_id,
            dst_label=self._entity.entity_name,
            edge_name=self._edge_name,
            neo=self._neo,
        ).call()

        edges += struct_edge.edges

        return edges

    def _node_id(self, data_link: models.DataLink) -> str:
        return f"{data_link.name_slug_str}:{self._entity.type_value}"
