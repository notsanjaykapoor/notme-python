import datetime
import typing

import pydantic
import sqlalchemy
import sqlmodel


class VariantPrule(sqlmodel.SQLModel, table=True):  # type: ignore
    __tablename__ = "variant_prules"

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    batch_id: int = sqlmodel.Field(index=False, nullable=True)  # ui ?
    case_size: int = sqlmodel.Field(index=False, nullable=True)
    category_id: int = sqlmodel.Field(index=False, nullable=True)  # single or tree
    dispensary_class_id: int = sqlmodel.Field(index=False, nullable=True)  # ?
    effect_amount: pydantic.condecimal(max_digits=20, decimal_places=10) = sqlmodel.Field(nullable=False)
    effect_operator: str = sqlmodel.Field(index=False, nullable=False)  # e.g. '+', '-', '='
    effect_unit: str = sqlmodel.Field(index=False, nullable=False)  # e.g. '$', '%'
    enabled: bool = sqlmodel.Field(index=False, nullable=False)
    end_time: datetime.datetime = sqlmodel.Field(sa_column=sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), index=False, nullable=True))
    order: int = sqlmodel.Field(index=False, nullable=True)  # ?
    override: bool = sqlmodel.Field(index=False, nullable=False)  # ?
    package_size: str = sqlmodel.Field(index=False, nullable=True)  # e.g. '1g'
    product_id: int = sqlmodel.Field(index=False, nullable=True)
    product_type: str = sqlmodel.Field(index=False, nullable=True)  # ?
    scope: str = sqlmodel.Field(index=False, nullable=False)  # e.g. 'item', 'order'
    start_time: datetime.datetime = sqlmodel.Field(sa_column=sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), index=False, nullable=True))
    stock_location_id: int = sqlmodel.Field(index=False, nullable=True)
    trigger_amount: pydantic.condecimal(max_digits=20, decimal_places=10) = sqlmodel.Field(nullable=False)
    trigger_operator: str = sqlmodel.Field(index=False, nullable=False)  # e.g. 'ge', 'gt', 'le', lt'
    trigger_unit: str = sqlmodel.Field(index=False, nullable=False)  # e.g. 'amount', 'quantity'
    variant_id: int = sqlmodel.Field(index=False, nullable=True)
    vendor_id: int = sqlmodel.Field(index=False, nullable=False)
    version: int = sqlmodel.Field(index=False, nullable=False)
