import logging
import neo4j
import os
import sys
import typing

from dataclasses import dataclass
from sqlmodel import select, Session

import models
import services.entities


@dataclass
class Struct:
    code: int
    node_count: int
    errors: typing.List[str]


class Slurp:
    def __init__(self, db: Session, offset: int = 0, limit: int = 1000):
        self._db = db
        self._offset = offset
        self._limit = limit

        self._model_properties = ["first_name", "last_name"]

        self._driver = services.neo.get_driver()

        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        # find unique slugs
        struct_slugs = services.entities.ListSlugs(db=self._db).call()

        for slug_tuple in struct_slugs.slugs:
            slug: str = slug_tuple[0]
            type_name: str = slug_tuple[1]

            # find unique type values with this slug value
            struct_values = services.entities.ListSlugValues(
                db=self._db,
                slug=slug,
            ).call()

            self._logger.info(f"{__name__} slug:{slug} {struct_values.values_count}")

            # filter out empty/none values
            slug_values = list(
                filter(lambda value: value is not None, struct_values.values)
            )

            node_count = self._create_node_targets(slug, type_name, slug_values)
            struct.node_count += node_count

        # find all unique entity ids
        struct_ids = services.entities.ListIds(db=self._db).call()

        for id in struct_ids.ids:
            # find entities
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
            target_entities = self._filter_target_entities(struct_list.entities)

            # create source node(s)

            node_count = self._create_node_source(
                entity_id, entity_name, source_entities
            )
            struct.node_count += node_count

            # create relationships between source and target nodes

            self._create_relationships(
                source_entity_id=entity_id,
                source_entity_name=entity_name,
                target_entities=target_entities,
            )

        self._close()

        return struct

    def _close(self):
        self._driver.close()

    def _create_node_source(
        self,
        entity_id: str,
        entity_name: str,
        entities: typing.List[models.Entity],
    ) -> int:
        """create source node with entity name as node name"""

        params = {
            "params": self._map_properties(entities) | {"id": entity_id},
        }

        # create node; note that node name can not be set with '$' format
        query = f"CREATE (p:{entity_name} $params) RETURN p.id"

        self._logger.info(f"{__name__} create {query} {params}")

        with self._driver.session() as session:
            result = session.write_transaction(self._create_with_tx, query, params)
            return 1

    def _create_node_targets(
        self,
        slug: str,
        type_name: str,
        values: typing.List[str],
    ) -> int:
        """create target nodes with entity slug as node name"""
        node_count = 0

        for value in values:
            node_params = {"value": value}

            # todo
            if type_name == "integer":
                # no quote
                node_params["value"] = int(value)  # type: ignore

            # node name is property slug; note that node name can not be set with '$' format
            query = f"CREATE (p:{slug} $params) RETURN p"

            params = {
                "params": node_params,
            }

            self._logger.info(f"{__name__} create {query} {params}")

            with self._driver.session() as session:
                session.write_transaction(self._create_with_tx, query, params)
                node_count += 1

        return node_count

    def _create_relationships(
        self,
        source_entity_id: str,
        source_entity_name: str,
        target_entities: typing.List[models.Entity],
    ) -> int:
        """create relationships between source node and target nodes"""

        node_count = 0

        for entity in target_entities:
            query = f"""
            MATCH (n1:{source_entity_name}), (n2:{entity.slug})
            WHERE n1.id = $source_entity_id and n2.value = $target_value
            CREATE (n1)-[r:HAS]->(n2)
            """

            if entity.type_name == "integer":
                target_value = int(entity.type_value)  # type: ignore
            else:
                target_value = entity.type_value.lower()  # type: ignore

            params = {
                "source_entity_id": source_entity_id,
                "target_value": target_value,
            }

            self._logger.info(f"{__name__} create {query} {params}")

            with self._driver.session() as session:
                session.write_transaction(self._create_with_tx, query, params)
                node_count += 1

        return node_count

    @staticmethod
    def _create_with_tx(tx: neo4j.Transaction, query: str, params: dict):
        return tx.run(query, params)

    def _filter_source_properties(
        self, entities: typing.List[models.Entity]
    ) -> typing.List[models.Entity]:
        """filter entities that should be added as graph node/model properties"""
        return list(
            filter(lambda entity: entity.slug in self._model_properties, entities)
        )

    def _filter_target_entities(
        self, entities: typing.List[models.Entity]
    ) -> typing.List[models.Entity]:
        """filter entities that should be added as graph nodes"""
        return list(
            filter(
                lambda entity: entity.slug not in self._model_properties
                and entity.type_value,
                entities,
            )
        )

    def _map_properties(self, entities: typing.List[models.Entity]) -> dict:
        dict = {}

        for entity in entities:
            # e.g. "first_name" => "joe", "last_name" => "bloggs"
            dict[entity.slug] = entity.type_value

        return dict
