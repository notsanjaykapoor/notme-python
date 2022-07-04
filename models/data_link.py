import typing

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class DataLink(SQLModel, table=True):  # type: ignore
    __tablename__ = "data_links"

    __table_args__ = (UniqueConstraint("src_name", "src_slug", "dst_name", "dst_slug", name="_src_dst_unique"),)

    id: typing.Optional[int] = Field(default=None, primary_key=True)

    src_name: str = Field(index=True)
    src_slug: str = Field(index=True)
    dst_name: str = Field(index=True)
    dst_slug: str = Field(index=True)

    @property
    def name_slug_str(self) -> str:
        return ":".join(list(sorted([f"{self.src_name}_{self.src_slug}", f"{self.dst_name}_{self.dst_slug}"])))

    def pack(self):
        return {
            "id": self.id,
            "src_name": self.src_name,
            "src_slug": self.src_slug,
            "dst_name": self.dst_name,
            "dst_slug": self.dst_slug,
        }
