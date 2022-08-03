import dataclasses
import typing

import shapely
import shapely.geometry
import sqlalchemy
import sqlmodel

import log
import models
import services.cities
import services.entities
import services.entity_locations


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

    def __init__(self, db: sqlmodel.Session, entity_ids: list[str, int]):
        self._db = db
        self._entity_ids = entity_ids

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, 0, [])

        self._logger.info(f"{__name__} using entity ids {self._entity_ids}")

        # find all matching entities and group by entity_id
        entity_list = services.entities.get_all_by_ids(db=self._db, ids=self._entity_ids)
        entity_groups = self._entities_group(entity_list)

        for entity_id in entity_groups.keys():
            entities = entity_groups[entity_id]
            entity = entities[0]

            # map entity set to an entity latlon
            entity_latlon = self._entity_latlon(entities)

            if entity_latlon.code != 0:
                struct.code = 422
                return struct

            entity_locations = services.entity_locations.get_all_by_entity_ids(db=self._db, ids=[entity.entity_id])

            if entity_locations:
                # entity location exists
                struct.code = 409
                return struct

            try:
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

            except sqlalchemy.exc.IntegrityError as e:
                self._db.rollback()
                struct.code = 409
                self._logger.error(f"{__name__} error {e}")
            except Exception as e:
                self._db.rollback()
                struct.code = 500
                self._logger.error(f"{__name__} exception {e}")

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

    def _entities_group(self, entities: list[models.Entity]) -> dict[str, list[models.Entity]]:
        """group entities by entity id"""
        group: dict[str, list[models.Entity]] = {}

        for entity in entities:
            if entity.entity_id not in group:
                group[entity.entity_id] = []

            group[entity.entity_id].append(entity)

        return group

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
