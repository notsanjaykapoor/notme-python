import dataclasses
import re
import typing

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
    node_start: typing.Optional[gql.types.GqlNode]
    nodes: list[gql.types.GqlNode]
    nodes_count: int
    edges: list[gql.types.GqlEdge]
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
        struct = Struct(0, None, [], 0, [], 0, [])

        self._logger.info(f"{context.rid_get()} {__name__} db query '{self._query}'")

        # tokenize query

        struct_tokens = services.mql.Parse(self._query).call()

        self._logger.info(f"{context.rid_get()} {__name__} db tokens {struct_tokens.tokens}")

        query_fields = [token["field"] for token in struct_tokens.tokens]

        if "start" in query_fields:
            records = self._nodes_match_start(tokens=struct_tokens.tokens)

            if not len(records):
                struct.code = 404
                return struct

            start = records[0]["node"]
            struct.node_start = self._gql_node(node=start, nid=start.id)
        else:
            records = self._nodes_match_all_with_edges()
            records += self._nodes_match_all_no_edges()

        if "radius" in query_fields:
            records += self._nodes_search(start, struct_tokens.tokens)

        # records keys can be 'node', 'edge', or 'path'
        records_node = [record for record in records if "node" in record.keys()]
        records_edge = [record for record in records if "edge" in record.keys()]
        records_path = [record for record in records if "path" in record.keys()]

        # parse 'node' records by nodes
        nodes_hash_base = self._nodes_by_id(records_node)

        # parse 'edge' records by edge ids
        edges_hash_base = self._edges_by_node_ids(records_edge)

        # parse 'path' records by nodes
        nodes_hash_path = self._path_nodes_by_id(records_path)

        # parse 'path' records by edge ids
        edges_hash_path = self._path_edges_by_node_ids(records_path)

        # merge results
        nodes_hash_merged = nodes_hash_base | nodes_hash_path
        edges_hash_merged = edges_hash_base | edges_hash_path

        # build nodes list
        for nid, node in nodes_hash_merged.items():
            gql_node = self._gql_node(node=node, nid=nid)
            struct.nodes.append(gql_node)

        # build edges list
        for key, edge in edges_hash_merged.items():
            src_nid, tgt_nid = key.split(":")

            gql_node_edge = gql.types.GqlEdge(
                name=edge.type,  # e.g. has, linked
                src_nid=src_nid,
                tgt_nid=tgt_nid,
            )  # type: ignore

            struct.edges.append(gql_node_edge)

        # sort nodes
        struct.nodes = sorted(struct.nodes, key=lambda object: self._result_object_sort(object))

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

    def _gql_node(self, node: neo4j.graph.Node, nid: str) -> gql.types.GqlNode:
        return gql.types.GqlNode(
            eid=node.get("id"),
            labels=sorted([label for label in node.labels]),
            name=node.get("name", ""),
            nid=nid,
        )  # type: ignore

    def _nodes_by_id(self, records: neo4j.Record) -> dict[str, neo4j.graph.Node]:
        """map records to hash of nodes indexed by node id"""
        nodes: dict[str, neo4j.graph.Node] = {}

        for record in records:
            node = record["node"]
            nodes[str(node.id)] = node

        return nodes

    def _nodes_match_all_no_edges(self) -> list[neo4j.Record]:
        """find all nodes without edges"""
        struct_graph = services.graph.query.match_all_no_edges()

        self._logger.info(f"{context.rid_get()} {__name__} neo query '{struct_graph.query}' params {struct_graph.params}")

        records = self._neo.read_transaction(services.graph.tx.read, struct_graph.query, struct_graph.params)

        return records

    def _nodes_match_all_with_edges(self) -> list[neo4j.Record]:
        """find all nodes with edges"""
        struct_graph = services.graph.query.match_all_with_edges()

        self._logger.info(f"{context.rid_get()} {__name__} neo query '{struct_graph.query}' params {struct_graph.params}")

        records = self._neo.read_transaction(services.graph.tx.read, struct_graph.query, struct_graph.params)

        return records

    def _nodes_match_start(self, tokens: list[dict]) -> list[neo4j.Record]:
        """find start node"""
        assert len(tokens)

        for token in tokens:
            field = token["field"]
            value = token["value"]

            if field == "start":
                struct_graph = services.graph.query.match_node(id=value)

                self._logger.info(f"{context.rid_get()} {__name__} neo query '{struct_graph.query}' params {struct_graph.params}")

                records = self._neo.read_transaction(services.graph.tx.read, struct_graph.query, struct_graph.params)

                return records

        return []

    def _nodes_search(self, start: neo4j.graph.Node, tokens: list[dict]) -> list[neo4j.Record]:
        assert len(tokens)

        for token in tokens:
            field = token["field"]
            value = token["value"]

            if field == "radius":
                match = re.match(r"^(\d+)h$", value)
                if not match:
                    raise ValueError("invalid radius")

                hops = match[1]

                node_labels = ":".join([label for label in start.labels])

                struct_graph = services.graph.query.match_neighbors(
                    src_label=node_labels,
                    src_id=start.get("id"),
                    max_hops=int(hops),
                )

                self._logger.info(f"{context.rid_get()} {__name__} neo query '{struct_graph.query}' params {struct_graph.params}")

                records = self._neo.read_transaction(services.graph.tx.read, struct_graph.query, struct_graph.params)

                return records

        return []

    def _path_edges_by_node_ids(self, records: neo4j.Record) -> dict[str, neo4j.graph.Relationship]:
        """map records to hash of edges indexed by node [start, end] ids"""

        edges: dict[str, neo4j.graph.Relationship] = {}

        for record in records:
            path = record["path"]

            for edge in path.relationships:
                node_start, node_end = edge.nodes
                key = ":".join(sorted([str(node_start.id), str(node_end.id)]))
                edges[key] = edge

        return edges

    def _path_nodes_by_id(self, records: neo4j.Record) -> dict[str, neo4j.graph.Node]:
        """map records to hash of nodes indexed by node id"""
        nodes: dict[str, neo4j.graph.Node] = {}

        for record in records:
            path = record["path"]
            for node in path.nodes:
                nodes[str(node.id)] = node

        return nodes

    def _result_object_sort(self, object: gql.types.GqlNode) -> str:
        if object.name:
            return object.name
        elif "property" in object.labels:
            return f"za{object.eid}"
        else:
            return f"zz{object.eid}"
