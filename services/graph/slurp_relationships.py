import logging
import neo4j
import sys
import typing

from dataclasses import dataclass
from sqlmodel import select, Session

import models
import services.entities


@dataclass
class Struct:
    code: int
    relationships_created: int
    errors: typing.List[str]


class SlurpRelationships:
    """Create graph relationships from entity node to 'slug' nodes"""

    def __init__(self, db: Session, driver: neo4j.Driver):
        self._db = db
        self._driver = driver

        self._entity_properties = ["first_name", "last_name"]
        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        # find all unique entity ids
        struct_ids = services.entities.ListIds(db=self._db).call()

        for id in struct_ids.ids:
            # find entities by entity_id
            struct_list = services.entities.List(
                db=self._db,
                query=f"entity_id:{id}",
                offset=0,
                limit=100,
            ).call()

            self._logger.info(f"{__name__} {struct_list.entities_count}")

            entities = struct_list.entities

            entity_id = entities[0].entity_id
            entity_name = entities[0].entity_name

            target_entities = self._filter_target_entities(entities)

            # create relationships between entity and target nodes

            relationships_created = self._create_node_relationships(
                source_entity_id=entity_id,
                source_entity_name=entity_name,
                target_entities=target_entities,
            )
            struct.relationships_created += relationships_created

        return struct

    def _create_node_relationships(
        self,
        source_entity_id: str,
        source_entity_name: str,
        target_entities: typing.List[models.Entity],
    ) -> int:
        """create relationships between entity node and target 'slug' nodes"""

        rel_created = 0

        for entity in target_entities:
            target_value = services.entities.graph_value_store(
                entity.type_name, str(entity.type_value)
            )

            params = {
                "source_entity_id": source_entity_id,
                "target_value": target_value,
            }

            query_exists = f"""
            MATCH (n1:{source_entity_name})-[r:has]-(n2:{entity.slug})
            WHERE n1.id = $source_entity_id and n2.value = $target_value
            RETURN count(r) as count
            """

            graph_count = self._get_graph_count(query_exists, params)

            if graph_count:
                # node exists
                return 0

            query_create = f"""
            MATCH (n1:{source_entity_name}), (n2:{entity.slug})
            WHERE n1.id = $source_entity_id and n2.value = $target_value
            CREATE (n1)-[r:has]->(n2)
            """

            self._logger.info(
                f"{__name__} create relationship entity {source_entity_name}:{source_entity_id} slug {entity.slug}"
            )

            with self._driver.session() as session:
                session.write_transaction(self._create_with_tx, query_create, params)
                rel_created += 1

        return rel_created

    @staticmethod
    def _create_with_tx(tx: neo4j.Transaction, query: str, params: dict):
        return tx.run(query, params)

    def _filter_target_entities(
        self, entities: typing.List[models.Entity]
    ) -> typing.List[models.Entity]:
        """filter entities that should be added as graph nodes"""
        return list(
            filter(
                lambda entity: entity.slug not in self._entity_properties
                and entity.type_value,
                entities,
            )
        )

    def _get_graph_count(self, query: str, params: dict) -> int:
        result = services.graph.query.execute(query, params, self._driver)
        return result[0]["count"]
