import re
import typing

import sqlalchemy
import sqlmodel

import models


def get_all_by_ids(db: sqlmodel.Session, ids: list[typing.Union[int, str]]) -> list[models.Entity]:
    dataset = sqlmodel.select(models.Entity)

    if re.match(r"^\d+$", str(ids[0])):
        dataset = dataset.where(models.Entity.id.in_(ids))  # type: ignore
    else:
        dataset = dataset.where(models.Entity.entity_id.in_(ids))  # type: ignore

    return db.exec(dataset).all()


def get_random(db: sqlmodel.Session) -> typing.Optional[models.Entity]:
    model = models.Entity
    dataset = sqlmodel.select(model).order_by(sqlalchemy.func.random()).limit(1)

    objects = db.exec(dataset).all()

    if not objects:
        return None

    return objects[0]
