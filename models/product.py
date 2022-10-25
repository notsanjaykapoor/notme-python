import typing

import pydantic
import sqlmodel


class Product(sqlmodel.SQLModel, table=True):  # type: ignore
    __tablename__ = "products"

    STATUS_ACTIVE = "active"
    STATUS_ARCHIVED = "archived"
    STATUS_DELETED = "deleted"

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    category_ids: list[int] = sqlmodel.Field(sa_column=sqlmodel.Column(sqlmodel.ARRAY(sqlmodel.INT)), default=[])
    description: str = sqlmodel.Field(index=False, nullable=False)
    name: str = sqlmodel.Field(index=True, nullable=False)
    price: pydantic.condecimal(max_digits=12, decimal_places=2) = sqlmodel.Field(nullable=False)
    status: str = sqlmodel.Field(index=True, nullable=False)
    vendor_id: int = sqlmodel.Field(index=False, nullable=False)
