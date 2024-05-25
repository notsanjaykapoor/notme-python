import sqlmodel

import models


def add(db_session: sqlmodel.Session, queue: str, partition: int, msg: str, data: dict) -> int:
    work_object = models.WorkQueue(
        data=data,
        msg=msg,
        name=queue,
        partition=partition,
        state=models.work_queue.STATE_QUEUED,
    )

    try:
        db_session.add(work_object)
        db_session.commit()
    except Exception:
        db_session.rollback()
        return 422

    return 0