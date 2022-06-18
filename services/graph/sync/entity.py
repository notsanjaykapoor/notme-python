import logging
from dataclasses import dataclass

import datadog
import neo4j
import sqlmodel

import services.graph
import services.graph.sync


@dataclass
class Struct:
    code: int
    nodes_created: int
    relationships_created: int
    errors: list[str]


class Entity:
    """
    sync entity to graph database
    """

    def __init__(self, db: sqlmodel.Session, driver: neo4j.Driver, entity_id: str):
        self._db = db
        self._driver = driver
        self._entity_id = entity_id

        self._logger = logging.getLogger("service")

    @datadog.statsd.timed(f"{__name__}.timer", tags=["env:dev"])
    def call(self) -> Struct:
        struct = Struct(0, 0, 0, [])

        entity = services.entities.get_by_id(db=self._db, id=self._entity_id)

        if not entity:
            struct.code = 404
            return struct

        struct_node_entity = services.graph.sync.CreateNodeEntity(
            driver=self._driver,
            entity=entity,
        ).call()

        struct.nodes_created += struct_node_entity.nodes_created

        struct_node_property = services.graph.sync.CreateNodeProperty(
            db=self._db,
            driver=self._driver,
            entity=entity,
        ).call()

        struct.nodes_created += struct_node_property.nodes_created

        struct_relationships_has = services.graph.sync.CreateRelationshipsHas(
            db=self._db,
            driver=self._driver,
            entity=entity,
        ).call()

        struct.relationships_created += struct_relationships_has.relationships_created

        struct_relationships_linked = services.graph.sync.CreateRelationshipsLinked(
            db=self._db,
            driver=self._driver,
            entity=entity,
        ).call()

        struct.relationships_created += struct_relationships_linked.relationships_created

        return struct