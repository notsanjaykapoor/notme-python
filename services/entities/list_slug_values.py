import logging
from dataclasses import dataclass

from sqlmodel import Session, select

import models


@dataclass
class Struct:
    code: int
    values: list[dict]
    values_count: int
    errors: list[str]


class ListSlugValues:
    def __init__(self, db: Session, slug: str):
        self._db = db
        self._slug = slug

        self._dataset = (
            select(
                models.Entity.entity_id,
                models.Entity.type_value,
            )
            .where(models.Entity.slug == self._slug)
            .distinct()
        )
        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        struct.values = [
            {
                "entity_id": object[0],
                "type_value": object[1],
            }
            for object in self._db.exec(self._dataset).all()
        ]
        struct.values_count = len(struct.values)

        return struct
