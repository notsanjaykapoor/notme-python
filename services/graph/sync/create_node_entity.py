import dataclasses
import logging

import datadog
import neo4j

import models
import services.graph
import services.graph.query
import services.graph.tx


@dataclasses.dataclass
class Struct:
    code: int
    nodes_created: int
    errors: list[str]


class CreateNodeEntity:
    """
    create graph node from entity object

    example: entity with name 'person' will result in graph node with label 'person', and id and name properties
    """

    def __init__(self, neo: neo4j.Session, entity: models.Entity):
        self._neo = neo
        self._entity = entity

        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        struct.nodes_created += self._create()

        return struct

    def _create(self) -> int:
        id = self._entity.entity_id
        label = self._entity.entity_name
        name = self._entity.name

        if self._entity.type_value is None:
            return 0

        query_exists = f"""
        match(n:{label} {{id: $id}}) return count(n) as count
        """

        params = {"id": id, "name": name}

        node_count = self._node_count(query_exists, params)

        if node_count:
            # node exists
            return 0

        # note that node label can not be set with '$' format
        query_create = f"create (p:{label} {{id: $id, name: $name}}) return p"

        self._logger.info(f"{__name__} label {label} props {params}")

        with datadog.statsd.timed(f"{__name__}.timer", tags=["env:dev", "neo:write"]):
            summary = self._neo.write_transaction(services.graph.tx.write, query_create, params)
            return summary.counters.nodes_created

    def _node_count(self, query: str, params: dict) -> int:
        result = services.graph.query.execute(query, params, self._neo)
        return result[0]["count"]
