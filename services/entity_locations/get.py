import sqlmodel

import models


def get_all_by_entity_ids(db: sqlmodel.Session, ids: list[str]) -> list[models.EntityLocation]:
    dataset = sqlmodel.select(models.EntityLocation).where(models.EntityLocation.entity_id.in_(ids))

    return db.exec(dataset).all()
