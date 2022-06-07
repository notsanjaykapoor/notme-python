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
    nodes_created: int
    errors: typing.List[str]


class SlurpEntity:
    """Create graph nodes for entity name and relationships to 'slug' nodes"""

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

            entity_id = struct_list.entities[0].entity_id
            entity_name = struct_list.entities[0].entity_name

            # partition entities

            source_entities = self._filter_source_properties(struct_list.entities)

            # create entity node(s)

            nodes_created = self._create_node_entity(
                entity_id, entity_name, source_entities
            )
            struct.nodes_created += nodes_created

        return struct

    def _create_node_entity(
        self,
        entity_id: str,
        entity_name: str,
        entities: typing.List[models.Entity],
    ) -> int:
        """create node labeled with entity_name"""

        params = {
            "params": self._map_properties(entities) | {"id": entity_id},
        }

        query_exists = (
            f"MATCH (p:{entity_name} "
            + "{id: "
            + f"'{entity_id}'"  # quote string
            + "}) RETURN count(p) as count"
        )

        node_count = self._get_node_count(query_exists, params)

        if node_count:
            # node exists
            return 0

        # create node; note that node label can not be set with '$' format
        query_create = f"CREATE (p:{entity_name} $params) RETURN p.id"

        self._logger.info(
            f"{__name__} create node:{entity_name} values:{params['params']}"
        )

        with self._driver.session() as session:
            result = session.write_transaction(
                self._create_with_tx, query_create, params
            )
            return 1

    @staticmethod
    def _create_with_tx(tx: neo4j.Transaction, query: str, params: dict):
        return tx.run(query, params)

    def _filter_source_properties(
        self, entities: typing.List[models.Entity]
    ) -> typing.List[models.Entity]:
        """filter entities that should be added as graph node/model properties"""
        return list(
            filter(lambda entity: entity.slug in self._entity_properties, entities)
        )

    def _get_node_count(self, query: str, params: dict) -> int:
        result = services.graph.query.execute(query, params, self._driver)
        return result[0]["count"]

    def _map_properties(self, entities: typing.List[models.Entity]) -> dict:
        dict = {}

        for entity in entities:
            # e.g. "first_name" => "joe", "last_name" => "bloggs"
            dict[entity.slug] = entity.type_value

        return dict
