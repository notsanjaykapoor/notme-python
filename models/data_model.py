import typing

from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint


class DataModel(SQLModel, table=True):  # type: ignore
    __tablename__ = "data_models"
    __table_args__ = (
        UniqueConstraint(
            "object_name", "object_slug", "object_type", name="_name_slug_type_unique"
        ),
    )

    id: typing.Optional[int] = Field(default=None, primary_key=True)

    object_name: str = Field(index=True)
    object_slug: str = Field(index=True)
    object_type: str = Field(index=True)

    def pack(self):
        return {
            "id": self.id,
            "object_name": self.object_name,
            "object_slug": self.object_slug,
            "object_type": self.object_type,
        }
