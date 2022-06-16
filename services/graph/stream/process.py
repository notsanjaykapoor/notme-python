import logging
from dataclasses import dataclass

import neo4j
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
            driver=self._driver,
            entity=self._entity,
        ).call()

        struct.nodes_created += struct_node_entity.nodes_created

        struct_node_property = services.graph.stream.CreateNodeProperty(
            db=self._db,
            driver=self._driver,
            entity=self._entity,
        ).call()

        struct.nodes_created += struct_node_property.nodes_created

        struct_relationships_has = services.graph.stream.CreateRelationshipsHas(
            db=self._db,
            driver=self._driver,
            entity=self._entity,
        ).call()

        struct.relationships_created += struct_relationships_has.relationships_created

        struct_relationships_linked = services.graph.stream.CreateRelationshipsLinked(
            db=self._db,
            driver=self._driver,
            entity=self._entity,
        ).call()

        struct.relationships_created += struct_relationships_linked.relationships_created

        return struct
