import typing

import datadog
import neo4j

import log
import services.entities
import services.graph
import services.graph.tx


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

    def call(self) -> int:
        query_exists = f"""
        match (a:{self._src_label})-[r:{self._edge_name}]-(b:{self._dst_label})
        where a.id = $src_id and b.id = $dst_id
        return count(r) as count
        """

        params = {
            "src_id": self._src_id,
            "dst_id": self._dst_id,
        }

        node_count = self._node_count(query_exists, params)

        if node_count:
            # node exists
            return 0

        query_create = f"""
        match (a:{self._src_label}), (b:{self._dst_label})
        where a.id = $src_id and b.id = $dst_id
        create (a)-[r:{self._edge_name}]->(b)
        """

        self._logger.info(f"{__name__} src {self._src_label}:{self._src_id} dst {self._dst_label}:{self._dst_id}")

        with datadog.statsd.timed(f"{__name__}.timer", tags=["env:dev", "neo:write"]):
            self._neo.write_transaction(services.graph.tx.write, query_create, params)
            return 1

    def _node_count(self, query: str, params: dict) -> int:
        result = services.graph.query.execute(query, params, self._neo)
        return result[0]["count"]
