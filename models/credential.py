import base64
import datetime
import typing

import sqlalchemy
import sqlmodel
from sqlmodel import Field, SQLModel


class Credential(SQLModel, table=True):  # type: ignore
    __tablename__ = "credentials"

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    name: str = sqlmodel.Field(index=True, nullable=False)
    public_key: str = Field(index=False, nullable=False)
    sign_count: int = Field(index=False, nullable=False)
    timestamp: datetime.datetime = Field(sa_column=sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), index=True, nullable=False))
    user_id: str = Field(index=True, nullable=False)
    webauthn_id: str = Field(index=True, nullable=False)

    @property
    def public_key_bytes(self) -> bytes:
        return base64.b64decode(self.public_key)

    @property
    def webauthn_bytes(self) -> bytes:
        return base64.b64decode(self.webauthn_id)

    def pack(self):
        return {
            "id": self.id,
            "name": self.name,  # user/system defined
            "public_key": self.public_key,
            "sign_count": self.sign_count,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
        }
