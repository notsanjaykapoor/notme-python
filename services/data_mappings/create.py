from dataclasses import dataclass

import sqlalchemy
import sqlmodel

import log
import models


@dataclass
class Struct:
    code: int
    ids: list[int]
    count: int
    errors: list[str]


class Create:
    def __init__(self, db: sqlmodel.Session, objects: list[dict]):
        self._db = db
        self._objects = objects

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        self._logger.info(f"{__name__} {self._objects}")

        try:
            for object in self._objects:
                db_object = models.DataMapping(
                    model_name=object["model_name"],
                    obj_mapping=object["obj_mapping"],
                    obj_name=object["obj_name"],
                    obj_pks=object["obj_pks"],
                )

                self._db.add(db_object)
                self._db.commit()

                if db_object.id:
                    struct.ids.append(db_object.id)
                    struct.count += 1
        except sqlalchemy.exc.IntegrityError as e:
            self._db.rollback()
            struct.code = 409

            self._logger.error(f"{__name__} integrity exception {e}")
        except Exception as e:
            self._db.rollback()
            struct.code = 422

            self._logger.error(f"{__name__} general exception {e}")

        return struct
