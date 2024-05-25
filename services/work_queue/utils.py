import sqlmodel

import models
import services.work_queue

def cleanup(db_session: sqlmodel.Session, queue: str, partition: int) -> int:
    """
    Reset all processing work objects as queued.

    Work objects can be left in a processing state during shutdown.
    """
    updated_count = 0

    list_result = services.work_queue.list(
        db_session=db_session,
        query=f"name:{queue} partition:{partition} state:{models.work_queue.STATE_PROCESSING}",
        offset=0,
        limit=10,
    )

    for work_object in list_result.objects:
        work_object.state = models.work_queue.STATE_QUEUED
        work_object.processing_at = None

        db_session.add(work_object)
        db_session.commit()

        updated_count += 1

    return updated_count