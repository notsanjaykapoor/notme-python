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
    nodes_created: int
    relationships_created: int
    errors: typing.List[str]


class Slurp:
    def __init__(self, db: Session):
        self._db = db

        self._driver = services.graph.get_driver()
        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, 0, [])

        struct_slugs = services.graph.SlurpSlugs(self._db, self._driver).call()
        struct.nodes_created += struct_slugs.nodes_created

        struct_entities = services.graph.SlurpEntity(self._db, self._driver).call()
        struct.nodes_created += struct_entities.nodes_created

        struct_relationships = services.graph.SlurpRelationships(
            self._db, self._driver
        ).call()

        struct.relationships_created += struct_relationships.relationships_created

        self._close()

        print(struct)

        return struct

    def _close(self):
        self._driver.close()
