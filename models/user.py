import typing

import sqlmodel

STATE_DISABLED = "disabled"
STATE_ENABLED = "enabled"


class User(sqlmodel.SQLModel, table=True):  # type: ignore
    __tablename__ = "users"

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    credentials_count: int = sqlmodel.Field(index=True, default=0)
    mobile: str = sqlmodel.Field(index=True, nullable=True)
    state: str = sqlmodel.Field(index=True, nullable=False)
    user_id: str = sqlmodel.Field(index=True, nullable=False)

    @property
    def emails_count(self) -> int:
        return 0

    @property
    def mobile_count(self) -> int:
        return 0

    def pack(self):
        return {
            "id": self.id,
            "mobile": self.mobile,
            "state": self.state,
            "user_id": self.user_id,
        }

    @property
    def totp_count(self) -> int:
        return 0
