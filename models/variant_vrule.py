import datetime
import typing

import pydantic
import sqlalchemy
import sqlmodel


class VariantVrule(sqlmodel.SQLModel, table=True):  # type: ignore
    __tablename__ = "variant_vrules"

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    batch_id: int = sqlmodel.Field(index=False, nullable=True)  # ui ?
    category_id: int = sqlmodel.Field(index=False, nullable=True)  # ?
    dispensary_class_id: int = sqlmodel.Field(index=False, nullable=True)  # ?
    enabled: bool = sqlmodel.Field(index=False, nullable=False)
    end_time: datetime.datetime = sqlmodel.Field(sa_column=sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), index=False, nullable=True))
    order: int = sqlmodel.Field(index=False, nullable=True)  # ?
    override: bool = sqlmodel.Field(index=False, nullable=False)  # ?
    package_size: str = sqlmodel.Field(index=False, nullable=True)  # e.g. '1g'
    product_id: int = sqlmodel.Field(index=False, nullable=True)  # mapped to variant_ids ?
    product_class_id: int = sqlmodel.Field(index=False, nullable=True)  # mapped to variant_ids ?
    start_time: datetime.datetime = sqlmodel.Field(sa_column=sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), index=False, nullable=True))
    stock_location_id: int = sqlmodel.Field(index=False, nullable=True)
    variant_id: int = sqlmodel.Field(index=False, nullable=True)
    visibility: str = sqlmodel.Field(index=False, nullable=False)  # 'enabled', 'private', 'disabled'
    vendor_id: int = sqlmodel.Field(index=False, nullable=True)  # ui ?
    version: int = sqlmodel.Field(index=False, nullable=False)
