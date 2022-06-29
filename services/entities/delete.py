import re
import typing

import sqlmodel

import models


def delete_by_id(db: sqlmodel.Session, ids: list[typing.Union[int, str]]) -> int:
    for id in ids:
        _delete(db, id)

    return 0


def _delete(db: sqlmodel.Session, id: typing.Union[int, str]) -> int:
    model = models.Entity
    dataset = sqlmodel.select(model)

    if re.match(r"^\d+$", str(id)):
        dataset = dataset.where(model.id == id)
    else:
        dataset = dataset.where(model.entity_id == id)

    objects = db.exec(dataset).all()

    for object in objects:
        db.delete(object)

    db.commit()

    return 0
