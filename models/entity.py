import typing

from sqlmodel import Field, SQLModel


class Entity(SQLModel, table=True):  # type: ignore
    __tablename__ = "entities"
    # __table_args__ = (
    #     UniqueConstraint("entity_id", "entity_name", name="_entity_unique"),
    # )

    id: typing.Optional[int] = Field(default=None, primary_key=True)
    entity_id: str = Field(index=True)
    entity_name: str = Field(index=True)
    slug: str = Field(index=True)
    type_name: str = Field(index=True)
    type_value: typing.Optional[str] = None

    def pack(self):
        return {
            "id": self.id,
            "entity_id": self.entity_id,  # [entity_id, entity_name] groups entities together
            "entity_name": self.entity_name,
            "slug": self.slug,
            "type_name": self.type_name,
            "type_value": self.type_value,
        }
