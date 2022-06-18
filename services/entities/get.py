import re
import typing

import sqlalchemy
import sqlmodel

import models


def get_by_id(db: sqlmodel.Session, id: typing.Union[int, str]) -> typing.Optional[models.Entity]:
    model = models.Entity
    dataset = sqlmodel.select(model)

    match = re.match(r"^\d+$", str(id))

    if match:
        dataset = dataset.where(model.id == id)
    else:
        dataset = dataset.where(model.entity_id == id)

    objects = db.exec(dataset).all()

    if not objects:
        return None

    return objects[0]


def get_random(db: sqlmodel.Session) -> typing.Optional[models.Entity]:
    model = models.Entity
    dataset = sqlmodel.select(model).order_by(sqlalchemy.func.random()).limit(1)

    objects = db.exec(dataset).all()

    if not objects:
        return None

    return objects[0]