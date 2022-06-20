import dataclasses
import logging
import typing

import datadog
import neo4j
import sqlmodel

import models
import services.entities
import services.graph
import services.graph.sync


@dataclasses.dataclass
class EntityPoint:
    code: int
    entity: typing.Optional[models.Entity]
    lat: float
    lon: float


@dataclasses.dataclass
class Struct:
    code: int
    nodes_updated: int
    errors: list[str]


class EntityGeo:
    """
    sync entity geo data with graph database
    """

    def __init__(self, db: sqlmodel.Session, neo: neo4j.Session, entity_id: str):
        self._db = db
        self._neo = neo
        self._entity_id = entity_id

        self._logger = logging.getLogger("service")

    @datadog.statsd.timed(f"{__name__}.timer", tags=["env:dev"])
    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        entity_point = self._entity_geo()

        if entity_point.code != 0:
            struct.code = entity_point.code
            return struct

        struct.nodes_updated += self._node_update(entity_point)

        return struct

    def _entity_geo(self) -> EntityPoint:
        """find entity and map to geo coords"""
        point = EntityPoint(1, None, 0, 0)

        entities = services.entities.get_all_by_id(db=self._db, id=self._entity_id)

        if not entities:
            return point

        entity_lat = [entity.type_value for entity in entities if entity.slug == "lat"]
        entity_lon = [entity.type_value for entity in entities if entity.slug == "lon"]

        if not entity_lat or not entity_lon:
            return point

        assert entity_lat[0]
        assert entity_lon[0]

        point.lat = float(entity_lat[0])
        point.lon = float(entity_lon[0])

        point.entity = entities[0]
        point.code = 0

        return point

    def _node_update(self, point: EntityPoint) -> int:
        assert point.entity

        entity = point.entity

        query_update = f"""
        match(n:{entity.entity_name} {{id: $id}}) set n.location = point({{latitude: $lat, longitude: $lon}})
        """

        params = {"id": entity.entity_id, "lat": point.lat, "lon": point.lon}

        self._logger.info(f"{__name__} label '{entity.entity_name}' props {params}")

        with datadog.statsd.timed(f"{__name__}.timer", tags=["env:dev", "neo:write"]):
            self._neo.write_transaction(services.graph.tx.write, query_update, params)

        return 1
