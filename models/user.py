import datetime
import os
import typing

import sqlalchemy
import sqlmodel

STATE_DISABLED = "disabled"
STATE_ENABLED = "enabled"


class User(sqlmodel.SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = (
        sqlalchemy.UniqueConstraint("email", name="_email"),
        sqlalchemy.UniqueConstraint("user_id", name="_user_id"),
    )

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    city: str = sqlmodel.Field(index=True, nullable=True)
    credentials_count: int = sqlmodel.Field(index=True, default=0)
    email: str = sqlmodel.Field(index=True, nullable=True)
    exported_at: datetime.datetime = sqlmodel.Field(
        nullable=True
    )  # syncing with search
    idp: str = sqlmodel.Field(
        index=True, default=""
    )  # identity provider, e.g. 'authentik', 'google'
    mobile: str = sqlmodel.Field(index=True, nullable=True)
    state: str = sqlmodel.Field(index=True, nullable=False)
    updated_at: datetime.datetime = sqlmodel.Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC), nullable=False
    )
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

    @classmethod
    def typesense_collection(cls) -> str:
        return f"users-{os.environ['TYPESENSE_ENV']}"

    def typesense_document(self) -> dict:
        return {
            "city": self.city or "",
            "email": self.email,
            "id": f"{self.id}",
            "location": [0.0, 0.0],
            "mobile": [self.mobile],
            "user_id": self.user_id,
        }

    @classmethod
    def typesense_schema(cls) -> dict:
        return {
            "name": cls.typesense_collection(),
            "fields": [
                {"name": "city", "type": "string", "facet": True},
                {"name": "email", "type": "string"},
                {"name": "location", "type": "geopoint"},
                {"name": "mobile", "type": "string[]"},
                {"name": "user_id", "type": "string"},
            ],
            "token_separators": ["+", "-", "@", "."],  # for email
        }
