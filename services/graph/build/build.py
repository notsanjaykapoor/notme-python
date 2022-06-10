import logging
import neo4j
import os
import sys
import typing

from dataclasses import dataclass
from sqlmodel import Session

import services.graph.build
import services.graph.driver


@dataclass
class Struct:
    code: int
    nodes_created: int
    relationships_created: int
    errors: typing.List[str]


class Build:
    def __init__(self, db: Session):
        self._db = db

        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, 0, [])

        with services.graph.driver.get() as driver:
            struct_entities = services.graph.build.BuildEntities(
                self._db, driver
            ).call()
            struct.nodes_created += struct_entities.nodes_created

            struct_slugs = services.graph.build.BuildEntitySlugs(
                self._db, driver
            ).call()
            struct.nodes_created += struct_slugs.nodes_created

            struct_connections = services.graph.build.BuildEntityConnections(
                self._db, driver
            ).call()
            struct.relationships_created += struct_connections.relationships_created

        return struct
