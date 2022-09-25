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
    def __init__(self, db: sqlmodel.Session, user_id: str, params: dict):
        self._db = db
        self._user_id = user_id
        self._params = params

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, None, [])

        self._logger.info(f"{context.rid_get()} {__name__} user_id {self._user_id}")

        db_object = models.User(
            city=self._params.get("city"),
            email=self._params.get("email"),
            mobile=self._params.get("mobile"),
            state=self._params.get("state"),
            user_id=self._user_id,
        )

        try:
            self._db.add(db_object)
            self._db.commit()

            struct.id = db_object.id
        except Exception as e:
            self._db.rollback()
            self._logger.error(f"{context.rid_get()} {__name__} exception {e}")
            raise e

        return struct
