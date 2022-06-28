import dataclasses
import typing

import sqlmodel

import models


@dataclasses.dataclass
class Struct:
    code: int
    ids: typing.List[str]
    count: int
    errors: typing.List[str]


class ListIds:
    def __init__(self, db: sqlmodel.Session):
        self._db = db

        self._dataset = sqlmodel.select(models.Entity.entity_id).distinct()

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        struct.ids = self._db.exec(self._dataset).all()
        struct.count = len(struct.ids)

        return struct
