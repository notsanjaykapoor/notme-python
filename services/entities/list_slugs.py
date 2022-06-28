import typing
from dataclasses import dataclass

from sqlmodel import Session, select

import models


@dataclass
class Struct:
    code: int
    slugs: typing.Tuple[str, str]
    slugs_count: int
    errors: typing.List[str]


class ListSlugs:
    def __init__(self, db: Session):
        self._db = db

        self._dataset = select(models.Entity.slug, models.Entity.type_name).distinct()

    def call(self) -> Struct:
        struct = Struct(0, ("", ""), 0, [])

        struct.slugs = self._db.exec(self._dataset).all()
        struct.slugs_count = len(struct.slugs)

        return struct
