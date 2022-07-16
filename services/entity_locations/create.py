import dataclasses
import sys
import typing

import shapely
import shapely.geometry
import sqlalchemy
import sqlmodel

import log
import models
import services.cities
import services.entities


@dataclasses.dataclass
class EntityLatLon:
    code: int
    lat: float
    lon: float


@dataclasses.dataclass
class Struct:
    code: int
    id: int
    count: int
    errors: list[str]


class Create:
    """create entity location from entity set"""

    def __init__(self, db: sqlmodel.Session, entity_ids: list[str]):
        self._db = db
        self._entity_ids = entity_ids

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, 0, [])

        self._logger.info(f"{__name__} {self._entity_ids}")

        for entity_id in self._entity_ids:
            entities = services.entities.get_all_by_id(db=self._db, id=entity_id)

            # map entity set to an entity latlon
            entity_latlon = self._entity_latlon(entities)

            if entity_latlon.code != 0:
                return struct

            try:
                entity = entities[0]
                point = f"Point({entity_latlon.lon} {entity_latlon.lat})"

                db_object = models.EntityLocation(
                    entity_id=entity.entity_id,
                    loc=point,
                )

                self._db.add(db_object)
                self._db.commit()

                if db_object.id:
                    struct.id = db_object.id
                    struct.count += 1

            except sqlalchemy.exc.IntegrityError:
                self._db.rollback()
                struct.code = 409
                self._logger.error(f"{__name__} {sys.exc_info()[0]} error")
            except Exception:
                self._db.rollback()
                struct.code = 500
                self._logger.error(f"{__name__} {sys.exc_info()[0]} exception")

        return struct

    def _city_point(self, name: str) -> typing.Optional[shapely.geometry.Point]:
        struct_list = services.cities.List(
            db=self._db,
            query=f"name:{name}",
            offset=0,
            limit=1,
        ).call()

        if not struct_list.count:
            return None

        return struct_list.objects[0].point

    def _entity_latlon(self, entities: list[models.Entity]) -> EntityLatLon:
        """map entity set to an entity latlon"""
        struct = EntityLatLon(0, 0, 0)

        entity_city = [entity.type_value for entity in entities if entity.slug == "city"]
        entity_lat = [entity.type_value for entity in entities if entity.slug == "lat"]
        entity_lon = [entity.type_value for entity in entities if entity.slug == "lon"]

        if entity_lat and entity_lon:
            # use entity lat, lon
            assert entity_lat[0]
            assert entity_lon[0]

            struct.lat = float(entity_lat[0])
            struct.lon = float(entity_lon[0])
        elif entity_city:
            # map city to lat, lon
            assert entity_city[0]

            point = self._city_point(name=entity_city[0].lower())

            if not point:
                struct.code = 422
                return struct

            struct.lat = point.y
            struct.lon = point.x
        else:
            struct.code = 422
            return struct

        return struct
