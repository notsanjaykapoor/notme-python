from typing import List, Optional

from sqlmodel import Field, Session, SQLModel


class User(SQLModel, table=True):  # type: ignore
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)

    def pack(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
        }
