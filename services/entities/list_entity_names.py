import dataclasses
import logging
import sqlmodel

import models


@dataclasses.dataclass
class Struct:
    code: int
    values: list[str]
    values_count: int
    errors: list[str]


class ListEntityNames:
    def __init__(self, db: sqlmodel.Session):
        self._db = db

        self._dataset = sqlmodel.select(
            models.Entity.entity_name,
        ).distinct()
        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        struct.values = self._db.exec(self._dataset).all()
        struct.values_count = len(struct.values)

        return struct
