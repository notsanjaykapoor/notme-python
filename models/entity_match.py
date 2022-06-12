import typing

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class EntityMatch(SQLModel, table=True):  # type: ignore
    __tablename__ = "entity_matches"
    __table_args__ = (
        UniqueConstraint("entity_id", "watch_id", name="_entity_watch_unique"),
    )

    id: typing.Optional[int] = Field(default=None, primary_key=True)
    entity_id: str = Field(index=True)
    watch_id: int = Field(index=True)

    def pack(self):
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "watch_id": self.watch_id,
        }
