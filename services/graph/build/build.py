import logging
import neo4j
import os
import sys
import typing

from dataclasses import dataclass
from sqlmodel import Session

import services.graph.build


@dataclass
class Struct:
    code: int
    nodes_created: int
    relationships_created: int
    errors: typing.List[str]


class Build:
    def __init__(self, db: Session):
        self._db = db

        self._driver = services.graph.get_driver()
        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, 0, [])

        struct_entities = services.graph.build.BuildEntity(
            self._db, self._driver
        ).call()

        struct.nodes_created += struct_entities.nodes_created

        struct_slugs = services.graph.build.BuildEntitySlugs(
            self._db, self._driver
        ).call()

        struct.nodes_created += struct_slugs.nodes_created

        struct_connections = services.graph.build.BuildEntityConnections(
            self._db, self._driver
        ).call()

        struct.relationships_created += struct_connections.relationships_created

        self._close()

        return struct

    def _close(self):
        self._driver.close()
