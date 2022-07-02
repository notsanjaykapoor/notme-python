import typing

import sqlmodel

STATE_DISABLED = "disabled"
STATE_ENABLED = "enabled"


class User(sqlmodel.SQLModel, table=True):  # type: ignore
    __tablename__ = "users"

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    mobile: str = sqlmodel.Field(index=True, nullable=False)
    state: str = sqlmodel.Field(index=True, nullable=False)
    user_id: str = sqlmodel.Field(index=True, nullable=False)

    def pack(self):
        return {
            "id": self.id,
            "mobile": self.mobile,
            "state": self.state,
            "user_id": self.user_id,
        }
