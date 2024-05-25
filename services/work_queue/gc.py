import sqlmodel

import models
import services.mql
import services.work_queue


def gc(db_session: sqlmodel.Session, queue: str, completed_before: int) -> int:
    """
    Garbage collect work queue objects completed before completed_before
    """
    work_objects = services.work_queue.list(
        db_session=db_session,
        query=f"name:{queue} state:{models.work_queue.STATE_COMPLETED} completed_at:<{completed_before}",
        limit=1024,
        offset=0,
    )

    deleted = 0

    for work_object in work_objects:
        db_session.delete(work_object)
        db_session.commit()

        deleted += 1

    return deleted