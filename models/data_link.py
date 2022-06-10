import typing

from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint


class DataLink(SQLModel, table=True):  # type: ignore
    __tablename__ = "data_links"
    __table_args__ = (
        UniqueConstraint(
            "src_name", "src_slug", "dst_name", "dst_slug", name="_src_dst_unique"
        ),
    )

    id: typing.Optional[int] = Field(default=None, primary_key=True)

    src_name: str = Field(index=True)
    src_slug: str = Field(index=True)
    dst_name: str = Field(index=True)
    dst_slug: str = Field(index=True)

    def pack(self):
        return {
            "id": self.id,
            "src_name": self.src_name,
            "src_slug": self.src_slug,
            "dst_name": self.dst_name,
            "dst_slug": self.dst_slug,
        }
