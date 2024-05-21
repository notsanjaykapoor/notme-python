import datetime
import typing

import sqlalchemy
import sqlmodel

STATE_INGESTED: str = "ingested"
STATE_PROCESSING: str = "processing"
STATE_QUEUED: str = "queued"

class Corpus(sqlmodel.SQLModel, table=True):
    __tablename__ = "corpus"
    __table_args__ = (
        sqlalchemy.UniqueConstraint("name", name="_name"),
    )

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    created_at: datetime.datetime = sqlmodel.Field(default_factory=datetime.datetime.utcnow, nullable=False)
    docs_count: int = sqlmodel.Field(index=True, nullable=False)
    embed_dims: int = sqlmodel.Field(index=True, nullable=False)
    embed_model: str = sqlmodel.Field(index=True, nullable=False)
    epoch: int = sqlmodel.Field(index=True, nullable=False)
    files_count: int = sqlmodel.Field(index=True, nullable=False)
    meta: dict = sqlmodel.Field(default_factory=dict, sa_column=sqlmodel.Column(sqlmodel.JSON))
    name: str = sqlmodel.Field(index=True, nullable=False) # fully encoded collection name
    nodes_count: int = sqlmodel.Field(index=True, nullable=False)
    org_id: int = sqlmodel.Field(index=True, nullable=False)
    signature: str = sqlmodel.Field(index=False, nullable=False)
    source_dir: str = sqlmodel.Field(index=True, nullable=False)
    state: str = sqlmodel.Field(index=True, nullable=False)
    updated_at: datetime.datetime = sqlmodel.Field(default_factory=datetime.datetime.utcnow, nullable=False)

    @property
    def indices(self) -> dict:
        return self.meta.get("indices", {}).keys()

    @property
    def keyword_doc_store(self) -> str:
        return self.meta.get("indices", {}).get("keyword", {}).get("doc_store", "")

    @property
    def keyword_index_store(self) -> str:
        return self.meta.get("indices", {}).get("keyword", {}).get("idx_store", "")

    @property
    def keyword_tables(self) -> list[str]:
        return [
            f"data_{self.keyword_doc_store}",
            f"data_{self.keyword_index_store}",
        ]

    @property
    def splitter(self) -> str:
        return self.meta.get("splitter") or ""
