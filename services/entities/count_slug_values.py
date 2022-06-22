import collections
import dataclasses
import logging
import typing

import sqlalchemy
import sqlmodel

import models

Tuple = collections.namedtuple("Tuple", ["slug", "value", "count"])


@dataclasses.dataclass
class Struct:
    code: int
    objects: list[Tuple]
    count: int
    errors: typing.List[str]


class CountSlugValues:
    def __init__(self, db: sqlmodel.Session, node: int):
        self._db = db
        self._node = node

        self._dataset = (
            sqlmodel.select(
                models.Entity.slug,
                models.Entity.type_value,
                sqlalchemy.func.count(models.Entity.type_value),
            )
            .group_by(models.Entity.slug, models.Entity.type_value)
            .where(models.Entity.node == self._node)
            .distinct()
        )
        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        struct.objects = [Tuple(*object) for object in self._db.exec(self._dataset).all()]
        struct.count = len(struct.objects)

        return struct
