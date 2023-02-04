import typing

import pydantic
import sqlmodel


class Variant(sqlmodel.SQLModel, table=True):
    __tablename__ = "variants"

    STATUS_ENABLED = "enabled"
    STATUS_PRIVATE = "private"
    STATUS_DISABLED = "disabled"

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    name: str = sqlmodel.Field(index=True, nullable=False)
    price: pydantic.condecimal(max_digits=12, decimal_places=2) = sqlmodel.Field(
        nullable=False
    )
    product_id: int = sqlmodel.Field(index=False, nullable=False)
    sku: str = sqlmodel.Field(index=True, nullable=False)
    status: str = sqlmodel.Field(index=True, nullable=False)
    stock_location_ids: list[int] = sqlmodel.Field(
        sa_column=sqlmodel.Column(sqlmodel.ARRAY(sqlmodel.INT)), default=[]
    )
    vendor_id: int = sqlmodel.Field(index=False, nullable=False)
    version: int = sqlmodel.Field(index=False, nullable=False)
