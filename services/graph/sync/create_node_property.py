import dataclasses
import logging

import datadog
import neo4j
import sqlmodel

import models
import services.data_models
import services.entities
import services.graph
import services.graph.query
import services.graph.tx


@dataclasses.dataclass
class Struct:
    code: int
    nodes_created: int
    errors: list[str]


class CreateNodeProperty:
    """
    create graph node using data model rules

    if data model [entity name, entity slug] has object_node == 1, then create a graph node with:
        - label eq slug
        - id property eq entity value

    e.g. given entity ['person', 'record_id', '1'], create node with label 'record_id' and id property '1'
    """

    def __init__(self, db: sqlmodel.Session, neo: neo4j.Session, entity: models.Entity):
        self._db = db
        self._neo = neo
        self._entity = entity

        self._data_model_query = f"object_name:{self._entity.entity_name} object_slug:{self._entity.slug} object_node:1"
        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        # find any matching data models
        struct_data_models = services.data_models.List(
            db=self._db,
            query=self._data_model_query,
            offset=0,
            limit=1000,
        ).call()

        if not struct_data_models.objects:
            return struct

        # entity matched data model, create the graph node for this entity
        struct.nodes_created += self._create()

        return struct

    def _create(self) -> int:
        slug = self._entity.slug

        value = services.entities.graph_value_store(self._entity.type_name, str(self._entity.type_value))

        query_exists = f"""
            match(n:{slug} {{id: $id}}) return count(n) as count
        """

        params = {"id": value}

        if self._node_count(query_exists, params):
            return 0  # node exists

        # note that node label can not be set with '$' format
        query_create = f"create (n:{slug} {{id: $id}}) RETURN n"

        self._logger.info(f"{__name__} slug {slug} props {params}")

        with datadog.statsd.timed(f"{__name__}.timer", tags=["env:dev", "neo:write"]):
            summary = self._neo.write_transaction(services.graph.tx.write, query_create, params)
            return summary.counters.nodes_created

        return 1

    def _node_count(self, query: str, params: dict) -> int:
        result = services.graph.query.execute(query, params, self._neo)
        return result[0]["count"]
