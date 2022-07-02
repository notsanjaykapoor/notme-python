import dataclasses
import typing

import sqlmodel

import context
import log
import models


@dataclasses.dataclass
class Struct:
    code: int
    id: typing.Optional[int]
    errors: list[str]


class Create:
    def __init__(self, db: sqlmodel.Session, user_id: str, mobile: str):
        self._db = db
        self._user_id = user_id
        self._mobile = mobile
        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, None, [])

        self._logger.info(f"{context.rid_get()} {__name__} user_id {self._user_id}")

        db_object = models.User(
            mobile=self._mobile,
            state="enabled",
            user_id=self._user_id,
        )

        self._db.add(db_object)
        self._db.commit()

        struct.id = db_object.id

        return struct
