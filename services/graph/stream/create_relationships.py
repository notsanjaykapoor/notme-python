import logging
import typing

import neo4j

import models
import services.entities
import services.graph
import services.graph.tx


class CreateRelationships:
    """create graph relationship"""

    def __init__(
        self,
        src_id: str,
        src_name: str,
        dst_id: typing.Union[int, str],
        dst_name: str,
        rel_name: str,
        driver: neo4j.Driver,
    ):
        self._src_id = src_id
        self._src_name = src_name
        self._dst_id = dst_id
        self._dst_name = dst_name
        self._rel_name = rel_name
        self._driver = driver

        self._logger = logging.getLogger("service")

    def call(self) -> int:
        query_exists = f"""
        match (a:{self._src_name})-[r:{self._rel_name}]-(b:{self._dst_name})
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
        match (a:{self._src_name}), (b:{self._dst_name})
        where a.id = $src_id and b.id = $dst_id
        create (a)-[r:{self._rel_name}]->(b)
        """

        self._logger.info(
            f"{__name__} src {self._src_name}:{self._src_id} dst {self._dst_name}:{self._dst_id}"
        )

        with self._driver.session() as session:
            session.write_transaction(services.graph.tx.write, query_create, params)
            return 1

    def _node_count(self, query: str, params: dict) -> int:
        result = services.graph.query.execute(query, params, self._driver)
        return result[0]["count"]
