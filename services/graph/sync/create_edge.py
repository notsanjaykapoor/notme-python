import dataclasses
import typing

import neo4j

import log
import services.entities
import services.graph
import services.graph.tx


@dataclasses.dataclass
class Struct:
    code: int
    edges_created: int
    edges: list[dict]
    errors: list[str]


class CreateEdge:
    """create graph edge"""

    def __init__(
        self,
        src_id: str,
        src_label: str,
        dst_id: typing.Union[int, str],
        dst_label: str,
        edge_name: str,
        neo: neo4j.Session,
    ):
        self._src_id = src_id
        self._src_label = src_label
        self._dst_id = dst_id
        self._dst_label = dst_label
        self._edge_name = edge_name
        self._neo = neo

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [], [])

        query_exists = f"""
        match (a:{self._src_label})-[r:{self._edge_name}]-(b:{self._dst_label})
        where a.id = $src_id and b.id = $dst_id
        return count(r) as count
        """

        params = {
            "src_id": self._src_id,
            "dst_id": self._dst_id,
        }

        edge_count = self._edge_count(query_exists, params)

        if edge_count:
            # edge exists
            return struct

        query_create = f"""
        match (a:{self._src_label}), (b:{self._dst_label})
        where a.id = $src_id and b.id = $dst_id
        create (a)-[r:{self._edge_name}]->(b)
        """

        self._logger.info(f"{__name__} src {self._src_label}:{self._src_id} dst {self._dst_label}:{self._dst_id}")

        summary = self._neo.write_transaction(services.graph.tx.write, query_create, params)
        struct.edges_created = summary.counters.relationships_created

        if summary.counters.relationships_created:
            struct.edges.append({"s": self._src_id, "d": self._dst_id, "e": self._edge_name})

        return struct

    def _edge_count(self, query: str, params: dict) -> int:
        result = services.graph.query.execute(query, params, self._neo)
        return result[0]["count"]
