import dataclasses

import neo4j
import neo4j.graph
import sqlmodel
from sqlmodel.sql.expression import Select, SelectOfScalar

import context
import gql.types
import log
import services.graph.query
import services.graph.tx
import services.mql

# this disables the warning: SAWarning: Class SelectOfScalar will not make use of SQL compilation caching
SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore


@dataclasses.dataclass
class Struct:
    code: int
    nodes: list[gql.types.GqlNode]
    nodes_count: int
    edges: list[gql.types.GqlNodeEdge]
    edges_count: int
    errors: list[str]


class List:
    def __init__(self, db: sqlmodel.Session, neo: neo4j.Session, query: str = "", offset: int = 0, limit: int = 100):
        self._db = db
        self._neo = neo
        self._query = query
        self._offset = offset
        self._limit = limit

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [], 0, [])

        self._logger.info(f"{context.rid_get()} {__name__} db query '{self._query}'")

        # tokenize query

        struct_tokens = services.mql.Parse(self._query).call()

        # for token in struct_tokens.tokens:
        #     value = token["value"]

        self._logger.info(f"{context.rid_get()} {__name__} db tokens {struct_tokens.tokens}")

        struct_graph = services.graph.query.match_all(format="wide")

        self._logger.info(f"{context.rid_get()} {__name__} neo query '{struct_graph.query}'")

        records = self._neo.read_transaction(services.graph.tx.read, struct_graph.query, struct_graph.params)

        # parse records by nodes
        nodes_hash = self._nodes_by_id(records)

        # parse records by edges
        edges_hash = self._edges_by_node_ids(records)

        # build nodes list
        for gid, node in nodes_hash.items():
            gql_node = gql.types.GqlNode(
                eid=node.get("id"),
                gid=gid,
                labels=sorted([label for label in node.labels]),
                name=node.get("name", ""),
            )  # type: ignore

            struct.nodes.append(gql_node)

        # build edges list
        for key, edge in edges_hash.items():
            src_gid, tgt_gid = key.split(":")

            gql_node_edge = gql.types.GqlNodeEdge(
                name=edge.type,
                src_gid=src_gid,
                tgt_gid=tgt_gid,
            )  # type: ignore

            struct.edges.append(gql_node_edge)

        # sort nodes
        struct.nodes = sorted(struct.nodes, key=lambda object: self._object_sort(object))

        struct.nodes_count = len(struct.nodes)
        struct.edges_count = len(struct.edges)

        return struct

    def _edges_by_node_ids(self, records: neo4j.Record) -> dict[str, neo4j.graph.Relationship]:
        """map records to hash of edges indexed by node [start, end] ids"""

        edges: dict[str, neo4j.graph.Relationship] = {}

        for record in records:
            edge = record["edge"]
            node_start, node_end = edge.nodes

            key = ":".join(sorted([str(node_start.id), str(node_end.id)]))

            edges[key] = edge

        return edges

    def _nodes_by_id(self, records: neo4j.Record) -> dict[str, neo4j.graph.Node]:
        """map records to hash of nodes indexed by node id"""
        nodes: dict[str, neo4j.graph.Node] = {}

        for record in records:
            node = record["node"]
            nodes[str(node.id)] = node

        return nodes

    def _object_sort(self, object: gql.types.GqlNode) -> str:
        if object.name:
            return object.name
        elif "property" in object.labels:
            return f"za{object.eid}"
        else:
            return f"zz{object.eid}"
