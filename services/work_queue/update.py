import datetime

import sqlmodel

import models


def state_completed(db_session: sqlmodel.Session, work_object: models.WorkQueue) -> int:
    """
    Mark work object as completed
    """
    if work_object.state == models.work_queue.STATE_COMPLETED:
        return 409

    work_object.state = models.work_queue.STATE_COMPLETED
    work_object.completed_at = datetime.datetime.now(datetime.timezone.utc)

    db_session.add(work_object)
    db_session.commit()

    return 0


def state_error(db_session: sqlmodel.Session, work_object: models.WorkQueue) -> int:
    """
    Mark work object as error
    """
    if work_object.state == models.work_queue.STATE_ERROR:
        return 409

    work_object.state = models.work_queue.STATE_ERROR
    work_object.completed_at = datetime.datetime.now(datetime.timezone.utc)

    db_session.add(work_object)
    db_session.commit()

    return 0


def state_processing(db_session: sqlmodel.Session, work_object: models.WorkQueue) -> int:
    """
    Mark work object as processing
    """
    if work_object.state == models.work_queue.STATE_PROCESSING:
        return 409

    work_object.state = models.work_queue.STATE_PROCESSING
    work_object.processing_at = datetime.datetime.now(datetime.timezone.utc)

    db_session.add(work_object)
    db_session.commit()

    return 0