import datetime
import math

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

    id: int | None = sqlmodel.Field(default=None, primary_key=True)

    completed_at: datetime.datetime = sqlmodel.Field(nullable=True)
    created_at: datetime.datetime = sqlmodel.Field(default_factory=datetime.datetime.utcnow, nullable=False)
    data: dict = sqlmodel.Field(default_factory=dict, sa_column=sqlmodel.Column(sqlmodel.JSON))
    msg: str = sqlmodel.Field(index=False, nullable=False, max_length=50)
    name: str = sqlmodel.Field(index=False, nullable=False, max_length=50)
    partition: int = sqlmodel.Field(index=False, nullable=False)
    processing_at: datetime.datetime = sqlmodel.Field(nullable=True)
    state: str = sqlmodel.Field(index=True, nullable=False, max_length=50)
    updated_at: datetime.datetime = sqlmodel.Field(default_factory=datetime.datetime.utcnow, nullable=False)

    @property
    def meta_str(self) -> str:
        """
        return semi-structed metadata from work_queue object
        """
        corpus_id = self.data.get("corpus_id", '"')

        if corpus_id:
            return f"corpus : {corpus_id}"

        return ""

    @property
    def work_time(self) -> str:
        if not self.completed_at or not self.processing_at:
            return ""

        seconds = (self.completed_at - self.processing_at).seconds

        if seconds > 3600:
            hours = math.floor(seconds / 3600)
            seconds = seconds % 3600
            minutes = math.floor(seconds / 60)
            return f"{hours}h {minutes}m"
        elif seconds > 60:
            minutes = math.floor(seconds / 60)
            seconds = seconds % 60
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
