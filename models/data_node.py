import typing

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class DataNode(SQLModel, table=True):  # type: ignore
    __tablename__ = "data_nodes"
    __table_args__ = (UniqueConstraint("src_name", "src_slug", name="_src_unique"),)

    id: typing.Optional[int] = Field(default=None, primary_key=True)

    src_name: str = Field(index=True)
    src_slug: str = Field(index=True)

    def pack(self):
        return {
            "id": self.id,
            "src_name": self.src_name,
            "src_slug": self.src_slug,
        }
