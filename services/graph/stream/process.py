import logging
import neo4j

from dataclasses import dataclass
from sqlmodel import Session

import models
import services.graph
import services.graph.stream


@dataclass
class Struct:
    code: int
    nodes_created: int
    relationships_created: int
    errors: list[str]


class Process:
    def __init__(self, db: Session, driver: neo4j.Driver, entity: models.Entity):
        self._db = db
        self._driver = driver
        self._entity = entity

        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, 0, [])

        struct_node_entity = services.graph.stream.CreateNodeEntity(
            driver=self._driver, entity=self._entity
        ).call()

        struct.nodes_created += struct_node_entity.nodes_created

        struct_node_rules = services.graph.stream.CreateNodeRules(
            db=self._db, driver=self._driver, entity=self._entity
        ).call()

        struct.nodes_created += struct_node_rules.nodes_created

        struct_relationships = services.graph.stream.CreateRelationshipsHas(
            db=self._db, driver=self._driver, entity=self._entity
        ).call()

        struct.relationships_created += struct_relationships.relationships_created

        struct_relationships = services.graph.stream.CreateRelationshipsLinked(
            db=self._db, driver=self._driver, entity=self._entity
        ).call()

        struct.relationships_created += struct_relationships.relationships_created

        return struct
