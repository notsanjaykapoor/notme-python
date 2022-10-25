import typing

import sqlmodel


class Category(sqlmodel.SQLModel, table=True):  # type: ignore
    __tablename__ = "categories"

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    level: int = sqlmodel.Field(index=False, nullable=False)  # level eq 0 is root node
    name: str = sqlmodel.Field(index=False, nullable=False)
    parent_id: int = sqlmodel.Field(index=False, nullable=True)  # level eq 0 has no parent_id
    slug: str = sqlmodel.Field(index=False, nullable=False)
    tree_id: int = sqlmodel.Field(index=False, nullable=False)
