import dataclasses
import typing

import sqlmodel

import log
import models


@dataclasses.dataclass
class Struct:
    code: int
    id: typing.Optional[int]
    errors: list[str]


class Create:
    def __init__(self, db: sqlmodel.Session, user_id: str):
        self._db = db
        self._user_id = user_id
        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, None, [])

        self._logger.info(f"{__name__} user_id {self._user_id}")

        db_object = models.User(user_id=self._user_id)

        self._db.add(db_object)
        self._db.commit()

        struct.id = db_object.id

        return struct
