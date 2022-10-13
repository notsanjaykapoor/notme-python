import dataclasses
import re
import typing

import datadog
import neo4j
import neo4j.graph
import sqlmodel
from sqlmodel.sql.expression import Select, SelectOfScalar

import context
import gql.types
import log
import models
import services.cities
import services.graph.distance
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
    node_end: typing.Optional[gql.types.GqlNode]
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

    @datadog.statsd.timed("service", tags=[f"service:{__name__}"])
    def call(self) -> Struct:
        struct = Struct(0, None, None, [], 0, [], 0, [])

        self._logger.info(f"{context.rid_get()} {__name__} db query '{self._query}'")

        # tokenize query

        struct_tokens = services.mql.Parse(self._query).call()

        tokens = struct_tokens.tokens

        self._logger.info(f"{context.rid_get()} {__name__} tokens {tokens}")

        query_fields = [token["field"] for token in tokens]

        if "city" in query_fields:
            # e.g. city:chicago radius:3mi

            if "radius" not in query_fields:
                # invalid query
                struct.code = 422
                return struct

            city = self._tokens_match_city(tokens=tokens)

            if not city:
                struct.code = 404
                return struct

            records = self._search_around_city(city=city, tokens=tokens)
        elif "node" in query_fields:
            # e.g. node:person+1 radius:3h
            records = self._tokens_match_node(tokens=tokens)

            if not len(records):
                struct.code = 404
                struct.errors.append("node not found")
                return struct

            if len(records) > 1:
                struct.code = 422
                struct.errors.append("node is not unique")
                return struct

            node = records[0]["node"]

            # set start node
            struct.node_start = self._gql_node(node=node)

            if "radius" in query_fields:
                records += self._search_around_node(node, tokens)
        elif "path" in query_fields:
            # e.g. path:person+1,person+2
            records = self._nodes_match_paths(tokens=tokens)

            if len(records):
                # set start and end nodes
                path = records[0]["path"]
                struct.node_start = self._gql_node(node=path.start_node)
                struct.node_end = self._gql_node(node=path.end_node)

        else:
            records = self._nodes_match_all_with_edges()
            records += self._nodes_match_all_no_edges()

        # records keys can be 'node', 'edge', or 'path'
        records_node = [record for record in records if "node" in record.keys()]
        records_edge = [record for record in records if "edge" in record.keys()]
        records_path = [record for record in records if "path" in record.keys()]

        # parse 'node' records by nodes
        nodes_hash_base = self._record_nodes_by_id(records_node)

        # parse 'edge' records by edge ids
        edges_hash_base = self._record_edges_by_node_ids(records_edge)

        # parse 'path' records by nodes and edge ids
        nodes_hash_path = self._path_nodes_by_id(records_path)
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

    def _gql_node(self, node: neo4j.graph.Node, nid: typing.Optional[str] = None) -> gql.types.GqlNode:
        """convert neo4j node to gql node object returned to caller"""
        point = node.get("location", None)

        if point:
            lat = point.y
            lon = point.x
        else:
            lat = 0.0
            lon = 0.0

        return gql.types.GqlNode(
            eid=node.get("id"),
            labels=sorted([label for label in node.labels]),
            lat=lat,
            lon=lon,
            name=node.get("name", self._gql_node_name(node)),
            nid=nid or node.id,
        )  # type: ignore

    def _gql_node_name(self, node: neo4j.graph.Node) -> str:
        if models.entity.LABEL_PROPERTY in node.labels:
            return node.get("id")
        else:
            return ""

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

    def _nodes_match_id(self, id: str) -> list[neo4j.Record]:
        """return records matching node id"""
        struct_graph = services.graph.query.match_node(id=id)

        self._logger.info(f"{context.rid_get()} {__name__} neo query '{struct_graph.query}' params {struct_graph.params}")

        return self._neo.read_transaction(services.graph.tx.read, struct_graph.query, struct_graph.params)

    def _nodes_match_paths(self, tokens: list[dict]) -> list[neo4j.Record]:
        """return all shortest paths"""
        assert len(tokens)

        for token in tokens:
            field = token["field"]
            value = token["value"]

            if field == "path":
                # e.g. path:person+1,person+2
                id_1, id_2 = map(lambda id: id.strip(), value.split(","))

                records_1 = self._nodes_match_id(id=id_1)
                records_2 = self._nodes_match_id(id=id_2)

                if not len(records_1) or not len(records_2):
                    raise ValueError("invalid path node")

                node_1 = records_1[0]["node"]
                node_2 = records_2[0]["node"]

                node_1_labels = ":".join([label for label in node_1.labels])
                node_2_labels = ":".join([label for label in node_2.labels])

                struct_graph = services.graph.query.match_shortest_path(
                    src_label=node_1_labels,
                    src_id=node_1.get("id"),
                    dst_label=node_2_labels,
                    dst_id=node_2.get("id"),
                )

                self._logger.info(f"{context.rid_get()} {__name__} neo query '{struct_graph.query}' params {struct_graph.params}")

                records = self._neo.read_transaction(services.graph.tx.read, struct_graph.query, struct_graph.params)

                return records

        return []

    def _path_edges_by_node_ids(self, records: neo4j.Record) -> dict[str, neo4j.graph.Relationship]:
        """map path records to hash of edges indexed by node [start, end] ids"""

        edges: dict[str, neo4j.graph.Relationship] = {}

        for record in records:
            path = record["path"]

            for edge in path.relationships:
                node_start, node_end = edge.nodes
                key = ":".join(sorted([str(node_start.id), str(node_end.id)]))
                edges[key] = edge

        return edges

    def _path_nodes_by_id(self, records: neo4j.Record) -> dict[str, neo4j.graph.Node]:
        """map path records to hash of nodes indexed by node id"""
        nodes: dict[str, neo4j.graph.Node] = {}

        for record in records:
            path = record["path"]
            for node in path.nodes:
                nodes[str(node.id)] = node

        return nodes

    def _record_edges_by_node_ids(self, records: neo4j.Record) -> dict[str, neo4j.graph.Relationship]:
        """map records to hash of edges indexed by node [start, end] ids"""

        edges: dict[str, neo4j.graph.Relationship] = {}

        for record in records:
            edge = record["edge"]
            node_start, node_end = edge.nodes
            key = ":".join(sorted([str(node_start.id), str(node_end.id)]))
            edges[key] = edge

        return edges

    def _record_nodes_by_id(self, records: neo4j.Record) -> dict[str, neo4j.graph.Node]:
        """map records to hash of nodes indexed by node id"""
        nodes: dict[str, neo4j.graph.Node] = {}

        for record in records:
            node = record["node"]
            nodes[str(node.id)] = node

        return nodes

    def _result_object_sort(self, object: gql.types.GqlNode) -> str:
        if object.name:
            return object.name
        elif models.entity.LABEL_PROPERTY in object.labels:
            return f"za{object.eid}"
        else:
            return f"zz{object.eid}"

    def _search_around_city(self, city: models.City, tokens: list[dict]) -> list[neo4j.Record]:
        assert len(tokens)

        records = []

        for token in tokens:
            field = token["field"]
            value = token["value"]

            if field == "radius":
                match = re.match(r"^(\d+)(ho|mi?)$", value)

                if not match:
                    raise ValueError("invalid radius")

                unit = match[2]

                if unit == "mi":
                    # map "3mi" to meters
                    meters = services.graph.distance.meters(value)

                    struct_graph = services.graph.query.match_geo_all_from_point(
                        lat=city.point.y,
                        lon=city.point.x,
                        meters=meters,
                    )
                else:
                    raise ValueError("invalid radius")

                self._logger.info(f"{context.rid_get()} {__name__} neo query '{struct_graph.query}' params {struct_graph.params}")

                records += self._neo.read_transaction(services.graph.tx.read, struct_graph.query, struct_graph.params)

        return records

    def _search_around_node(self, node: neo4j.graph.Node, tokens: list[dict]) -> list[neo4j.Record]:
        assert len(tokens)

        records = []

        for token in tokens:
            field = token["field"]
            value = token["value"]

            if field == "radius":
                match = re.match(r"^(\d+)(ho|mi?)$", value)

                if not match:
                    raise ValueError("invalid radius")

                num = int(match[1])
                unit = match[2]

                node_labels = ":".join([label for label in node.labels])

                struct_graph: services.graph.query.types.GraphQuery

                if unit == "ho":
                    struct_graph = services.graph.query.match_neighbors(
                        src_label=node_labels,
                        src_id=node.get("id"),
                        max_hops=num,
                    )
                elif unit == "mi":
                    # map "3mi" to meters
                    meters = services.graph.distance.meters(value)

                    struct_graph = services.graph.query.match_geo_all_from_node(
                        src_label=node_labels,
                        src_id=node.get("id"),
                        meters=meters,
                    )
                else:
                    raise ValueError("invalid radius")

                self._logger.info(f"{context.rid_get()} {__name__} neo query '{struct_graph.query}' params {struct_graph.params}")

                records += self._neo.read_transaction(services.graph.tx.read, struct_graph.query, struct_graph.params)

        return records

    def _tokens_match_city(self, tokens: list[dict]) -> typing.Optional[models.City]:
        """find city token and map to a city object"""
        assert len(tokens)

        for token in tokens:
            field = token["field"]

            if field == "city":
                struct_list = services.cities.List(
                    db=self._db,
                    query=f"name:{token['value']}",
                    offset=0,
                    limit=1,
                ).call()

                return struct_list.objects[0]

        return None

    def _tokens_match_node(self, tokens: list[dict]) -> list[neo4j.Record]:
        """find node token and map to a set of records"""
        assert len(tokens)

        for token in tokens:
            field = token["field"]

            if field == "node":
                return self._nodes_match_id(id=token["value"])

        return []
