import sqlalchemy
import sqlmodel

import models


def get_max_version(db: sqlmodel.Session) -> int:
    version = db.exec(sqlalchemy.func.max(models.Entity.version)).scalar()

    if version is None:
        version = -1

    return version
