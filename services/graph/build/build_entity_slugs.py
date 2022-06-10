import logging
import neo4j
import sys
import typing

from dataclasses import dataclass
from sqlmodel import Session

import models
import services.entities


@dataclass
class Struct:
    code: int
    nodes_created: int
    errors: typing.List[str]


class BuildEntitySlugs:
    """Create graph nodes for entity slugs"""

    def __init__(self, db: Session, driver: neo4j.Driver):
        self._db = db
        self._driver = driver

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

            self._logger.info(
                f"{__name__} slug:{slug} values:{struct_values.values_count}"
            )

            # filter out empty/none values
            slug_values = list(
                filter(
                    lambda dict: dict["type_value"] is not None, struct_values.values
                )
            )

            # create nodes
            nodes_created = self._create_nodes(slug, type_name, slug_values)

            struct.nodes_created += nodes_created

        return struct

    def _create_nodes(
        self,
        slug: str,
        type_name: str,
        values: list[dict],
    ) -> int:
        """create nodes labeled with 'slug' with with specified values"""
        nodes_created = 0

        for dict in values:
            entity_id = dict["entity_id"]
            type_value = dict["type_value"]

            value_store = services.entities.graph_value_store(type_name, type_value)
            value_query = services.entities.graph_value_query(type_name, type_value)

            # node name is property slug:
            # note - that node label can not be set with '$' format
            # note - parameter maps cannot be used in match patterns
            query_exists = (
                f"MATCH (p:{slug} "
                + "{value: "
                + f"{value_query}"
                + ", id: "
                + f"'{entity_id}'"
                + "}) RETURN count(p) as count"
            )

            node_count = self._get_node_count(query_exists, {})

            if node_count:
                # node exists
                continue

            params_create = {
                "params": {
                    "id": entity_id,
                    "value": value_store,
                },
            }

            # node name is property slug; note that node label can not be set with '$' format
            query_create = f"CREATE (p:{slug} $params) RETURN p"

            self._logger.info(f"{__name__} slug:{slug} props:{dict}")

            with self._driver.session() as session:
                session.write_transaction(
                    self._create_nodes_with_tx, query_create, params_create
                )
                nodes_created += 1

        return nodes_created

    @staticmethod
    def _create_nodes_with_tx(tx: neo4j.Transaction, query: str, params: dict):
        return tx.run(query, params)

    def _get_node_count(self, query: str, params: dict) -> int:
        result = services.graph.query.execute(query, {}, self._driver)
        return result[0]["count"]
