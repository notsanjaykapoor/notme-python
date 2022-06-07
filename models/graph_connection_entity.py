import typing

from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint


class GraphConnectionEntity(SQLModel, table=True):  # type: ignore
    __tablename__ = "graph_entity_connections"
    __table_args__ = (
        UniqueConstraint(
            "entity_name", "entity_slug", "rel_name", name="_entity_rel_unique"
        ),
    )

    id: typing.Optional[int] = Field(default=None, primary_key=True)
    entity_name: str = Field(index=True)
    entity_slug: str = Field(index=True)
    rel_name: str = Field(index=True)

    def pack(self):
        return {
            "id": self.id,
            "entity_name": self.entity_name,
            "entity_slug": self.entity_slug,
            "rel_name": self.rel_name,
        }
