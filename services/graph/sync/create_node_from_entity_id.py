import dataclasses

import datadog
import neo4j

import log
import models
import services.graph.query
import services.graph.tx


@dataclasses.dataclass
class Struct:
    code: int
    nodes_created: int
    errors: list[str]


ENTITY_SLUG_ID = "id"

NODE_LABEL = "entity"


class CreateNodeFromEntityId:
    """
    create graph node from entity object id

    example: entity with name 'person' will map to a graph node labeled 'person:entity', with id and name properties
    """

    def __init__(self, neo: neo4j.Session, entity: models.Entity):
        self._neo = neo
        self._entity = entity

        self._node_id = self._entity.entity_id
        self._node_labels = f"{self._entity.entity_name}:{NODE_LABEL}"
        self._node_name = self._entity.name

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        if (self._entity.node == 0) or (self._entity.slug != ENTITY_SLUG_ID):
            return struct

        struct.nodes_created += self._node_create()

        return struct

    def _node_count(self, query: str, params: dict) -> int:
        result = services.graph.query.execute(query, params, self._neo)
        return result[0]["count"]

    def _node_create(self) -> int:
        if self._entity.type_value is None:
            return 0

        query_exists = f"""
        match(n:{self._node_labels} {{id: $id}}) return count(n) as count
        """

        params = {"id": self._node_id, "name": self._node_name}

        node_count = self._node_count(query_exists, params)

        if node_count:
            # node exists
            return 0

        # note that node label can not be set with '$' format
        query_create = f"create (p:{self._node_labels} {{id: $id, name: $name}}) return p"

        self._logger.info(f"{__name__} label {self._node_labels} props {params}")

        with datadog.statsd.timed(f"{__name__}.timer", tags=["env:dev", "neo:write"]):
            summary = self._neo.write_transaction(services.graph.tx.write, query_create, params)
            return summary.counters.nodes_created
