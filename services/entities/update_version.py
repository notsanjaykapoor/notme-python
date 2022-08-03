import sqlmodel

import models


def update_version(db: sqlmodel.Session, entity_id: str, version: int) -> int:
    rows_updated = db.query(models.Entity).filter(models.Entity.entity_id == entity_id).update({models.Entity.version: version})
    db.commit()
    return rows_updated
