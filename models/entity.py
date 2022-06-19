import typing

from sqlmodel import Field, SQLModel


class Entity(SQLModel, table=True):  # type: ignore
    __tablename__ = "entities"

    id: typing.Optional[int] = Field(default=None, primary_key=True)
    entity_id: str = Field(index=True)
    entity_key: str = Field(index=True)
    entity_name: str = Field(index=True)
    name: str = Field(index=True)
    slug: str = Field(index=True)
    tags: str = Field(default="||")
    type_name: str = Field(index=True)  # e.g. string
    type_value: typing.Optional[str] = None

    def pack(self):
        return {
            "id": self.id,
            "entity_id": self.entity_id,  # [entity_id, entity_name, entity_key] groups entities together
            "entity_key": self.entity_key,
            "entity_name": self.entity_name,
            "name": self.name,
            "slug": self.slug,
            "tags": self.tags,
            "type_name": self.type_name,
            "type_value": self.type_value,
        }

    def message_changed(self) -> dict:
        return {
            "id": self.id,  # id is unique, entity_id is not
            "name": "entity.changed",
        }

    @classmethod
    def message_changed_cls(cls, id: int) -> dict:
        return {
            "id": id,
            "name": "entity.changed",
        }

    @classmethod
    def message_geo_changed_cls(cls, id: str) -> dict:
        return {
            "id": id,
            "name": "entity.geo.changed",
        }
