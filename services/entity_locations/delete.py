import sqlmodel

import models


def delete_by_id(db: sqlmodel.Session, ids: list[int]) -> int:
    model = models.EntityLocation
    dataset = sqlmodel.select(model).where(model.id.in_(ids))

    objects = db.exec(dataset).all()

    for object in objects:
        db.delete(object)

    db.commit()

    return 0
