import sqlmodel

import models


def delete_by_id(db: sqlmodel.Session, ids: list[int]) -> int:
    model = models.City
    dataset = sqlmodel.select(model)

    dataset = dataset.where(model.id.in_(ids))  # type: ignore

    objects = db.exec(dataset).all()

    for object in objects:
        db.delete(object)

    db.commit()

    return 0
