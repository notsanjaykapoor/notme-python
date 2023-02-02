import sqlmodel

import models
import services.database


def delete_by_id(db: sqlmodel.Session, ids: list[int]) -> int:
    model = models.User
    dataset = sqlmodel.select(model)

    dataset = dataset.where(model.id.in_(ids))  # type: ignore

    objects = db.exec(dataset).all()

    for object in objects:
        db.delete(object)

    db.commit()

    return 0


def truncate(db: sqlmodel.Session):
    table_names = ["users"]

    for table_name in table_names:
        services.database.truncate_table(db=db, table_name=table_name)
