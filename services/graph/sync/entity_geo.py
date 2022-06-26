import dataclasses
import logging

import datadog
import neo4j
import sqlmodel

import models
import services.entities
import services.entity_locations
import services.graph
import services.graph.sync


@dataclasses.dataclass
class EntityLatLon:
    code: int
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

        # vaidate entity
        entities = services.entities.get_all_by_id(db=self._db, id=self._entity_id)

        if not entities:
            struct.code = 404
            return struct

        # map geo coords to an entity location object
        entity_latlon = self._entity_latlon(entities)

        if entity_latlon.code != 0:
            struct.code = entity_latlon.code
            return struct

        # update graph database
        struct.nodes_updated += self._node_update(
            entity_latlon=entity_latlon,
            entity_name=entities[0].entity_name,
        )

        return struct

    def _entity_latlon(self, entities: list[models.Entity]) -> EntityLatLon:
        """map entity to an entity latlon"""
        struct = EntityLatLon(0, 0, 0)

        entity_lat = [entity.type_value for entity in entities if entity.slug == "lat"]
        entity_lon = [entity.type_value for entity in entities if entity.slug == "lon"]

        if not entity_lat or not entity_lon:
            struct.code = 422
            return struct

        assert entity_lat[0]
        assert entity_lon[0]

        struct.lat = float(entity_lat[0])
        struct.lon = float(entity_lon[0])

        return struct

    def _node_update(self, entity_latlon: EntityLatLon, entity_name: str) -> int:
        query_update = f"""
        match(n:{entity_name} {{id: $id}}) set n.location = point({{latitude: $lat, longitude: $lon}})
        """

        params = {"id": self._entity_id, "lat": entity_latlon.lat, "lon": entity_latlon.lon}

        self._logger.info(f"{__name__} label '{entity_name}' props {params}")

        with datadog.statsd.timed(f"{__name__}.timer", tags=["env:dev", "neo:write"]):
            self._neo.write_transaction(services.graph.tx.write, query_update, params)

        return 1
