import typing

import sqlmodel


class VendorStockLocation(sqlmodel.SQLModel, table=True):  # type: ignore
    __tablename__ = "vendor_stock_locations"

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    name: str = sqlmodel.Field(index=True, nullable=False)
    vendor_id: int = sqlmodel.Field(index=False, nullable=False)
