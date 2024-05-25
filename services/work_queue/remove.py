import sqlmodel

import models


def remove(db_session: sqlmodel.Session, id: int,) -> int:
    work_object = db_session.exec(
        sqlmodel.select(models.WorkQueue).where(models.WorkQueue.id == id)
    ).first()

    if not work_object:
        return 404

    db_session.delete(work_object)
    db_session.commit()

    return 0