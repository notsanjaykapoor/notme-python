import logging
import typing
from dataclasses import dataclass

import datadog
import neo4j
import sqlmodel

import models
import services.entities
import services.graph
import services.graph.sync


@dataclass
class Point:
    code: int
    entity: typing.Optional[models.Entity]
    lat: float
    lon: float


@dataclass
class Struct:
    code: int
    nodes_updated: int
    errors: list[str]


class EntityGeo:
    """
    sync entity geo data to graph database
    """

    def __init__(self, db: sqlmodel.Session, driver: neo4j.Driver, entity_id: str):
        self._db = db
        self._driver = driver
        self._entity_id = entity_id

        self._logger = logging.getLogger("service")

    @datadog.statsd.timed(f"{__name__}.timer", tags=["env:dev"])
    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        entity = services.entities.get_by_id(db=self._db, id=self._entity_id)

        if not entity:
            struct.code = 404
            return struct

        point = self._entity_geo(entity.entity_id)

        if point.code != 0:
            struct.code = point.code
            return struct

        struct.nodes_updated += self._node_update(point)

        return struct

    def _entity_geo(self, entity_id: str) -> Point:
        """find entity and map to geo coords"""
        point = Point(1, None, 0, 0)

        struct_list = services.entities.List(
            db=self._db,
            query=f"entity_id:{entity_id}",
            offset=0,
            limit=100,
        ).call()

        entity_lat = [object.type_value for object in struct_list.objects if object.slug == "lat"]
        entity_lon = [object.type_value for object in struct_list.objects if object.slug == "lon"]

        if not entity_lat or not entity_lon:
            return point

        assert entity_lat[0]
        assert entity_lon[0]

        point.entity = struct_list.objects[0]
        point.lat = float(entity_lat[0])
        point.lon = float(entity_lon[0])
        point.code = 0

        return point

    def _node_update(self, point: Point) -> int:
        assert point.entity

        id = point.entity.entity_id
        label = point.entity.entity_name

        query_update = f"""
        match(n:{label} {{id: $id}}) set n.location = point({{latitude: $lat, longitude: $lon, crs: "WGS-84"}})
        """

        params = {"id": id, "lat": point.lat, "lon": point.lon}

        self._logger.info(f"{__name__} label {label} props {params}")

        with self._driver.session() as session:
            session.write_transaction(services.graph.tx.write, query_update, params)

        return 1
