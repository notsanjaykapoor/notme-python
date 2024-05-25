import sqlmodel

import models


def get_queued(db_session: sqlmodel.Session, queue: str, partition: int) -> models.WorkQueue | None:
    """
    Get the next work queue object for the specified queue and partition
    """
    model = models.WorkQueue

    work_object = db_session.exec(
        sqlmodel
            .select(model)
            .where(model.name == queue).where(model.partition == partition).where(model.state == models.work_queue.STATE_QUEUED)
            .order_by(model.id.asc())
    ).first()

    return work_object
