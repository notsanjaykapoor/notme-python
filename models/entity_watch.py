import typing

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class EntityWatch(SQLModel, table=True):  # type: ignore
    __tablename__ = "entity_watches"
    __table_args__ = (UniqueConstraint("name", "query", name="_name_query_unique"),)

    id: typing.Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    query: str = Field(index=True)
    route: str = Field(index=True)

    def pack(self):
        return {
            "id": self.id,
            "name": self.name,
            "query": self.query,
            "route": self.route,
        }
