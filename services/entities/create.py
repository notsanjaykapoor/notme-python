import dataclasses

import sqlalchemy
import sqlmodel

import log
import models
import services.entities
import services.entity_locations


@dataclasses.dataclass
class Struct:
    code: int
    ids: list[int]
    count: int
    entity_ids: set[str]
    entity_count: int
    location_ids: list[int]
    errors: list[str]


class Create:
    """create entity"""

    def __init__(self, db: sqlmodel.Session, entities: list[models.Entity]):
        self._db = db
        self._entities = entities

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, set(), 0, [], [])

        self._logger.info(f"{__name__} {self._entities}")

        try:
            for entity in self._entities:
                self._db.add(entity)

            self._db.commit()

            for entity in self._entities:
                if entity.id:
                    struct.ids.append(entity.id)
                    struct.count += 1
                    struct.entity_ids.add(entity.entity_id)
                    struct.entity_count = len(struct.entity_ids)

            # create entity locations
            struct_locations = services.entity_locations.Create(
                db=self._db,
                entity_ids=list(struct.ids),
            ).call()

            if struct_locations.code == 0:
                struct.location_ids.append(struct_locations.id)
        except sqlalchemy.exc.IntegrityError as e:
            self._db.rollback()
            struct.code = 409
            self._logger.error(f"{__name__} error {e}")
        except Exception as e:
            self._db.rollback()
            struct.code = 500
            self._logger.error(f"{__name__} exception {e}")

        return struct
