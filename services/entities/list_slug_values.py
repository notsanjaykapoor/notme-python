import logging
import re
import typing

from dataclasses import dataclass
from sqlmodel import select, Session

import models


@dataclass
class Struct:
    code: int
    values: typing.List[str]
    values_count: int
    errors: typing.List[str]


class ListSlugValues:
    def __init__(self, db: Session, slug: str):
        self._db = db
        self._slug = slug

        self._dataset = (
            select(models.Entity.type_value)
            .where(models.Entity.slug == self._slug)
            .distinct()
        )
        self._logger = logging.getLogger("api")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        struct.values = self._db.exec(self._dataset).all()
        struct.values_count = len(struct.values)

        return struct
