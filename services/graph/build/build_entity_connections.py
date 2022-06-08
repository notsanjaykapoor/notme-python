import logging
import neo4j
import sys
import typing

from dataclasses import dataclass
from sqlmodel import select, Session

import models
import services.entities
import services.graph


@dataclass
class Struct:
    code: int
    relationships_created: int
    errors: typing.List[str]


class BuildEntityConnections:
    """Create graph relationships using GraphConnectionEntity rules"""

    def __init__(self, db: Session, driver: neo4j.Driver):
        self._db = db
        self._driver = driver

        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        struct_connections = services.graph.connections.List(
            db=self._db, query="", offset=0, limit=100
        ).call()

        for connection in struct_connections.objects:
            offset = 0
            limit = 100

            # find entities by name and slug
            while True:
                struct_entities = services.entities.List(
                    db=self._db,
                    query=f"entity_name:{connection.entity_name} slug:{connection.entity_slug}",
                    offset=offset,
                    limit=limit,
                ).call()

                if not struct_entities.entities:
                    break

                rel_created = self._create_node_relationships(
                    entities=struct_entities.entities
                )

                struct.relationships_created += rel_created

                offset += limit

        return struct

    def _create_node_relationships(self, entities: typing.List[models.Entity]) -> int:
        """create relationships between entity node and target 'slug' nodes"""

        rel_created = 0

        for entity in entities:
            # check for empty values
            if not entity.type_value:
                continue

            target_value = services.entities.graph_value_store(
                entity.type_name, str(entity.type_value)
            )

            params = {
                "entity_id": entity.entity_id,
                "target_value": target_value,
            }

            query_exists = f"""
            MATCH (n1:{entity.entity_name})-[r:has]-(n2:{entity.slug})
            WHERE n1.id = $entity_id and n2.value = $target_value
            RETURN count(r) as count
            """

            graph_count = self._get_graph_count(query_exists, params)

            if graph_count:
                # node exists
                return 0

            query_create = f"""
            MATCH (n1:{entity.entity_name}), (n2:{entity.slug})
            WHERE n1.id = $entity_id and n2.value = $target_value
            CREATE (n1)-[r:has]->(n2)
            """

            self._logger.info(
                f"{__name__} create relationship entity {entity.entity_name}:{entity.entity_id} slug {entity.slug}"
            )

            with self._driver.session() as session:
                session.write_transaction(self._create_with_tx, query_create, params)
                rel_created += 1

        return rel_created

    @staticmethod
    def _create_with_tx(tx: neo4j.Transaction, query: str, params: dict):
        return tx.run(query, params)

    def _get_graph_count(self, query: str, params: dict) -> int:
        result = services.graph.query.execute(query, params, self._driver)
        return result[0]["count"]
