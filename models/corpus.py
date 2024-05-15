import datetime
import typing

import sqlalchemy
import sqlmodel

STATE_INGESTED: str = "ingested"

class Corpus(sqlmodel.SQLModel, table=True):
    __tablename__ = "corpus"
    __table_args__ = (
        sqlalchemy.UniqueConstraint("collection_name", name="_collection_name"),
    )

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    collection_name: str = sqlmodel.Field(index=True, nullable=False) # fully encoded collection name
    created_at: datetime.datetime = sqlmodel.Field(default_factory=datetime.datetime.utcnow, nullable=False)
    docs_count: int = sqlmodel.Field(index=True, nullable=False)
    dims_count: int = sqlmodel.Field(index=True, nullable=False)
    embed_name: str = sqlmodel.Field(index=True, nullable=False)
    nodes_count: int = sqlmodel.Field(index=True, nullable=False)
    org_id: int = sqlmodel.Field(index=True, nullable=False)
    state: str = sqlmodel.Field(index=True, nullable=False)
    updated_at: datetime.datetime = sqlmodel.Field(default_factory=datetime.datetime.utcnow, nullable=False)