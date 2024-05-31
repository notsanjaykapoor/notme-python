import datetime
import typing

import sqlalchemy
import sqlmodel

STATE_DIRTY: str = "dirty"
STATE_DRAFT: str = "draft"
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
    fingerprint: str = sqlmodel.Field(index=False, nullable=False)
    meta: dict = sqlmodel.Field(default_factory=dict, sa_column=sqlmodel.Column(sqlmodel.JSON))
    name: str = sqlmodel.Field(index=True, nullable=False) # fully encoded name
    nodes_count: int = sqlmodel.Field(index=True, nullable=False)
    org_id: int = sqlmodel.Field(index=True, nullable=False)
    source_uri: str = sqlmodel.Field(index=True, nullable=False)
    state: str = sqlmodel.Field(index=True, nullable=False)
    updated_at: datetime.datetime = sqlmodel.Field(default_factory=datetime.datetime.utcnow, nullable=False)

    @property
    def ingestable(self) -> int:
        if self.state in ["dirty", "ingested"]:
            return 0
        return 1

    @property
    def queryable(self) -> int:
        if self.state in ["dirty", "ingested"]:
            return 0
        return 1

    @property
    def splitter(self) -> str:
        return self.meta.get("splitter") or ""

    @property
    def storage_keyword(self) -> dict:
        """keyword storage metadata"""
        return self.meta.get("storage", {}).get("keyword", {})

    @property
    def storage_keyword_tables(self) -> list[str]:
        """keyword storage postgres tables"""
        ks = self.storage_keyword
        return [
            f"data_{ks.get('doc_store')}",
            f"data_{ks.get('idx_store')}",
        ]

    @property
    def storage_meta(self) -> dict:
        """get storage metadata"""
        return self.meta.get("storage", {})
