import datetime

import sqlalchemy
import sqlmodel


class Event(sqlmodel.SQLModel, table=True):
    """create timescale events table; primary key should be a datetime field"""

    __tablename__ = "events"

    class Config:
        arbitrary_types_allowed = True

    name: str = sqlmodel.Field(index=True)
    timestamp: datetime.datetime = sqlmodel.Field(
        sa_column=sqlalchemy.Column(
            sqlalchemy.DateTime(timezone=True),
            primary_key=True,
            index=True,
            nullable=False,
        )
    )
    value: float = sqlmodel.Field(index=True)
