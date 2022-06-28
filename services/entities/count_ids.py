import dataclasses
import typing

import sqlalchemy
import sqlmodel

import models


@dataclasses.dataclass
class Struct:
    code: int
    count: int
    errors: typing.List[str]


class CountIds:
    def __init__(self, db: sqlmodel.Session):
        self._db = db

        self._dataset = sqlmodel.select([sqlalchemy.func.count(models.Entity.entity_id.distinct())])  # type: ignore

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        struct.count = self._db.exec(self._dataset).all()[0]

        return struct
