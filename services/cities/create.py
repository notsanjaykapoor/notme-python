import dataclasses

import sqlalchemy
import sqlmodel

import log
import models


@dataclasses.dataclass
class EntityLatLon:
    code: int
    lat: float
    lon: float


@dataclasses.dataclass
class Struct:
    code: int
    ids: list[int]
    count: int
    errors: list[str]


class Create:
    """create city"""

    def __init__(self, db: sqlmodel.Session, objects: list[dict]):
        self._db = db
        self._objects = objects

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        self._logger.info(f"{__name__} {self._objects}")

        for object in self._objects:
            try:
                name = object["name"].lower()
                point = f"Point({object['lon']} {object['lat']})"

                db_object = models.City(
                    name=name,
                    loc=point,
                )

                self._db.add(db_object)
                self._db.commit()

                if db_object.id:
                    struct.ids.append(db_object.id)
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
