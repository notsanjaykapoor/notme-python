import dataclasses
import logging
import typing

import sqlmodel

import models
from context import request_id


@dataclasses.dataclass
class Struct:
    code: int
    user: typing.Optional[models.User]
    errors: list[str]


class Get:
    def __init__(self, db: sqlmodel.Session, user_id: str):
        self._db = db
        self._user_id = user_id

        self._model = models.User
        self._logger = logging.getLogger("api")

    def call(self) -> Struct:
        struct = Struct(0, None, [])

        self._logger.info(f"{request_id.get()} {__name__} {self._user_id}")

        struct.user = self._db.exec(sqlmodel.select(self._model).where(self._model.user_id == self._user_id)).first()

        if struct.user is None:
            struct.code = 404

        return struct
