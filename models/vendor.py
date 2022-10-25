import typing

import sqlmodel


class Vendor(sqlmodel.SQLModel, table=True):  # type: ignore
    __tablename__ = "vendors"

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    name: str = sqlmodel.Field(index=False, nullable=False)
    slug: str = sqlmodel.Field(index=False, nullable=False)
