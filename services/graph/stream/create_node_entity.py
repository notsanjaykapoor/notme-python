import logging
from dataclasses import dataclass

import neo4j

import models
import services.graph
import services.graph.query
import services.graph.tx


@dataclass
class Struct:
    code: int
    nodes_created: int
    errors: list[str]


class CreateNodeEntity:
    """
    create graph node from entity object

    example: entity with name 'person' will result in graph node with label 'person' and id property
    """

    def __init__(self, driver: neo4j.Driver, entity: models.Entity):
        self._driver = driver
        self._entity = entity

        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        struct.nodes_created += self._create()

        return struct

    def _create(self) -> int:
        entity_id = self._entity.entity_id
        name = self._entity.entity_name

        if self._entity.type_value is None:
            return 0

        query_exists = f"""
            match(n:{name} {{id: $entity_id}}) return count(n) as count
        """

        params = {"entity_id": entity_id}

        node_count = self._node_count(query_exists, params)

        if node_count:
            # node exists
            return 0

        # note that node label can not be set with '$' format
        query_create = f"create (p:{name} {{id: $entity_id}}) return p"

        self._logger.info(f"{__name__} slug {name} props {params}")

        with self._driver.session() as session:
            session.write_transaction(services.graph.tx.write, query_create, params)

        return 1

    def _node_count(self, query: str, params: dict) -> int:
        result = services.graph.query.execute(query, params, self._driver)
        return result[0]["count"]
