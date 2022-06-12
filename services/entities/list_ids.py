import logging
import re
import typing
from dataclasses import dataclass

from sqlmodel import Session, select

import models


@dataclass
class Struct:
    code: int
    ids: typing.List[str]
    ids_count: int
    errors: typing.List[str]


class ListIds:
    def __init__(self, db: Session):
        self._db = db

        self._dataset = select(models.Entity.entity_id).distinct()
        self._logger = logging.getLogger("api")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        struct.ids = self._db.exec(self._dataset).all()
        struct.ids_count = len(struct.ids)

        return struct
