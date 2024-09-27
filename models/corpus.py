import datetime
import os
import re
import typing

import pydantic
import sqlalchemy
import sqlmodel

MODEL_NAME_DEFAULT: str = "local:gte-large"
SPLITTER_NAME_DEFAULT: str = "chunk:1024:40"

STATE_DIRTY: str = "dirty"
STATE_DRAFT: str = "draft"
STATE_INGESTED: str = "ingested"
STATE_NEW: str = "new"
STATE_PROCESSING: str = "processing"
STATE_QUEUED: str = "queued"

class Corpus(sqlmodel.SQLModel, table=True):
    __tablename__ = "corpus"
    __table_args__ = (
        sqlalchemy.UniqueConstraint("name", name="_name"),
    )

    # remove warnings about fields named "model_"
    model_config = pydantic.ConfigDict(protected_namespaces=())

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    created_at: datetime.datetime = sqlmodel.Field(default_factory=lambda: datetime.datetime.now(datetime.UTC), nullable=False)
    docs_count: int = sqlmodel.Field(index=True, nullable=False)
    model_dims: int = sqlmodel.Field(index=False, nullable=False)
    model_name: str = sqlmodel.Field(index=False, nullable=False)
    epoch: int = sqlmodel.Field(index=True, nullable=False)
    files_count: int = sqlmodel.Field(index=True, nullable=False)
    fingerprint: str = sqlmodel.Field(index=False, nullable=False)
    meta: dict = sqlmodel.Field(default_factory=dict, sa_column=sqlmodel.Column(sqlmodel.JSON))
    name: str = sqlmodel.Field(index=True, nullable=False) # fully encoded name
    nodes_count: int = sqlmodel.Field(index=True, nullable=False)
    org_id: int = sqlmodel.Field(index=True, nullable=False)
    source_uri: str = sqlmodel.Field(index=True, nullable=False)
    splitter: str = sqlmodel.Field(index=False, nullable=True, default="")
    state: str = sqlmodel.Field(index=True, nullable=False)
    updated_at: datetime.datetime = sqlmodel.Field(default_factory=lambda: datetime.datetime.now(datetime.UTC), nullable=False)
    vector_img_uri: str = sqlmodel.Field(index=False, nullable=True, default="")
    vector_txt_uri: str = sqlmodel.Field(index=False, nullable=True, default="")

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
    def source_files(self) -> tuple[str, str]:
        """
        returns files in corpus source_uri
        """
        if not (match := re.match(r'^file:\/\/([^\/]+)\/(.+)$', self.source_uri)):
            raise ValueError(f"source_uri {self.source_uri} invalid")

        _source_host, source_path = (match[1], match[2])

        # match = re.match(r'^(.+)\/(.+)$$', source_path)
        # source_dir = match[1]

        # files are in local fs
        source_files = sorted([f"{source_path}/{file}" for file in os.listdir(source_path) if os.path.isfile(f"{source_path}/{file}")])

        return source_path, source_files

    @property
    def source_type(self) -> str:

        if self.vector_img_uri:
            return "multi"

        if self.vector_txt_uri:
            return "text"

        return ""

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
