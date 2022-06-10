import logging
import neo4j

from dataclasses import dataclass
from sqlmodel import Session

import models
import services.data_nodes
import services.entities
import services.graph
import services.graph.query
import services.graph.tx


@dataclass
class Struct:
    code: int
    nodes_created: int
    errors: list[str]


class CreateNodeRules:
    """
    create graph node from data node rules

    example: data node has [name,slug] == [person,record_id], then all matching 'person' entities with slug 'record_id'
    will result in graph nodes with label 'name' and id property 'slug'
    """

    def __init__(self, db: Session, driver: neo4j.Driver, entity: models.Entity):
        self._db = db
        self._driver = driver
        self._entity = entity

        self._data_link_query = (
            f"src_name:{self._entity.entity_name} src_slug:{self._entity.slug}"
        )
        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        # find matching data nodes
        struct_data_nodes = services.data_nodes.List(
            db=self._db,
            query=self._data_link_query,
            offset=0,
            limit=1000,
        ).call()

        if not struct_data_nodes.objects:
            return struct

        # entity matched at least 1 rule, create the rule object for this entity
        struct.nodes_created += self._create()

        return struct

    def _create(self) -> int:
        slug = self._entity.slug

        value = services.entities.graph_value_store(
            self._entity.type_name, str(self._entity.type_value)
        )

        query_exists = f"""
            match(n:{slug} {{id: $id}}) return count(n) as count
        """

        params = {"id": value}

        if self._node_count(query_exists, params):
            return 0  # node exists

        # note that node label can not be set with '$' format
        query_create = f"create (n:{slug} {{id: $id}}) RETURN n"

        self._logger.info(f"{__name__} slug {slug} props {params}")

        with self._driver.session() as session:
            session.write_transaction(services.graph.tx.write, query_create, params)

        return 1

    def _node_count(self, query: str, params: dict) -> int:
        result = services.graph.query.execute(query, params, self._driver)
        return result[0]["count"]
