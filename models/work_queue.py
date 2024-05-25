import datetime
import typing

import sqlalchemy
import sqlmodel


QUEUE_CORPUS_INGEST = "corpus-ingest"
QUEUE_CORPUS_INGEST_PARTITIONS = 1 # partition count == number of workers

STATE_COMPLETED = "completed"
STATE_ERROR = "error"
STATE_PROCESSING = "processing"
STATE_QUEUED = "queued"


class WorkQueue(sqlmodel.SQLModel, table=True):
    __tablename__ = "work_queue"
    __table_args__ = (sqlalchemy.Index("ix_name_partition", "name", "partition"),)

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)

    completed_at: datetime.datetime = sqlmodel.Field(default_factory=datetime.datetime.utcnow, nullable=True)
    created_at: datetime.datetime = sqlmodel.Field(default_factory=datetime.datetime.utcnow, nullable=False)
    data: dict = sqlmodel.Field(default_factory=dict, sa_column=sqlmodel.Column(sqlmodel.JSON))
    msg: str = sqlmodel.Field(index=False, nullable=False, max_length=50)
    name: str = sqlmodel.Field(index=False, nullable=False, max_length=50)
    partition: int = sqlmodel.Field(index=False, nullable=False)
    processing_at: datetime.datetime = sqlmodel.Field(default_factory=datetime.datetime.utcnow, nullable=True)
    state: str = sqlmodel.Field(index=True, nullable=False, max_length=50)
    updated_at: datetime.datetime = sqlmodel.Field(default_factory=datetime.datetime.utcnow, nullable=False)
