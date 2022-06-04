import logging

from dataclasses import dataclass
from sqlmodel import select, Session

from sqlmodel.sql.expression import Select, SelectOfScalar

SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

from context import request_id
from models.user import User


@dataclass
class Struct:
    code: int
    user: User
    errors: list[str]


class Get:
    def __init__(self, db: Session, user_id: str):
        self._db = db
        self._user_id = user_id

        self._logger = logging.getLogger("api")

    def call(self) -> Struct:
        struct = Struct(0, None, [])

        self._logger.info(f"{request_id.get()} {__name__} {self._user_id}")

        struct.user = self._db.exec(
            select(User).where(User.user_id == self._user_id)
        ).first()

        if struct.user is None:
            struct.code = 404

        return struct
