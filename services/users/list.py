import logging
import re

from dataclasses import dataclass
from sqlmodel import select, Session

from sqlmodel.sql.expression import Select, SelectOfScalar

SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

from context import request_id
from models.user import User
from services.mql.parse import MqlParse


@dataclass
class Struct:
    code: int
    users: list[User]
    errors: list[str]


@dataclass
class StructToken:
    code: int
    tokens: list[dict]
    errors: list[str]


class UsersList:
    def __init__(self, db: Session, query: str = "", offset: int = 0, limit: int = 20):
        self._db = db
        self._query = query
        self._offset = offset
        self._limit = limit

        self._dataset = select(User)  # default database query
        self._logger = logging.getLogger("api")

    def call(self):
        struct = Struct(0, [], [])

        self._logger.info(f"{request_id.get()} {__name__} query {self._query}")

        # tokenize query

        struct_tokens = MqlParse(self._query).call()

        self._logger.info(
            f"{request_id.get()} {__name__} tokens {struct_tokens.tokens}"
        )

        for token in struct_tokens.tokens:
            value = token["value"]

            if token["field"] == "user_id":
                match = re.match(r"^~", value)

                if match:
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(
                        User.user_id.like("%" + value_normal + "%")
                    )
                else:
                    # match query
                    self._dataset = self._dataset.where(User.user_id == value)

        struct.users = self._db.exec(
            self._dataset.offset(self._offset).limit(self._limit)
        ).all()

        return struct
