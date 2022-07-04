import dataclasses

import datadog
import neo4j
import sqlmodel

import log
import models
import services.data_models
import services.entities
import services.graph.query
import services.graph.tx


@dataclasses.dataclass
class Struct:
    code: int
    nodes_created: int
    errors: list[str]


ENTITY_SLUG_ID = "id"

NODE_LABEL = "property"


class CreateNodeFromEntitySlug:
    """
    create graph node if entity node value eq 1, with node label 'property' and node id as entity [slug, value]
    """

    def __init__(self, db: sqlmodel.Session, neo: neo4j.Session, entity: models.Entity):
        self._db = db
        self._neo = neo
        self._entity = entity

        self._node_label = NODE_LABEL
        self._node_id = f"{self._entity.slug}:{self._entity.type_value}"

        self._logger = log.init("service")

    def _node_count(self, query: str, params: dict) -> int:
        result = services.graph.query.execute(query, params, self._neo)
        return result[0]["count"]

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        # note: slug value 'id' is created separately
        if (self._entity.node == 0) or (self._entity.slug == ENTITY_SLUG_ID):
            return struct

        # create the graph node for this entity
        struct.nodes_created += self._node_create()

        return struct

    def _node_create(self) -> int:
        query_exists = f"""
        match(n:{self._node_label} {{id: $id}}) return count(n) as count
        """

        params = {"id": self._node_id}

        if self._node_count(query_exists, params):
            return 0  # node exists

        # note that node label can not be set with '$' format
        query_create = f"create (n:{self._node_label} {{id: $id}}) RETURN n"

        self._logger.info(f"{__name__} label {self._node_label} props {params}")

        with datadog.statsd.timed(f"{__name__}.timer", tags=["env:dev", "neo:write"]):
            summary = self._neo.write_transaction(services.graph.tx.write, query_create, params)
            return summary.counters.nodes_created

        return 1
