import dataclasses
import typing

import sqlmodel

import log
import models
import services.credentials


@dataclasses.dataclass
class Struct:
    code: int
    id: typing.Optional[int]
    errors: list[str]


class Create:
    def __init__(self, object: dict, db: sqlmodel.Session):
        self._object = object
        self._db = db

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, None, [])

        self._logger.info(f"{__name__} try")

        user_id = self._object.get("user_id")

        db_object = models.Credential(
            name=self._object.get("name"),
            public_key=self._object.get("public_key"),
            sign_count=self._object.get("sign_count"),
            timestamp=self._object.get("timestamp"),
            user_id=user_id,
            webauthn_id=self._object.get("webauthn_id"),
        )

        self._db.add(db_object)
        self._db.commit()

        struct.id = db_object.id

        assert user_id

        self._user_credentials_count_update(user_id)

        self._logger.info(f"{__name__} ok")

        return struct

    def _user_credentials_count_update(self, user_id: str) -> int:
        # get credentials count
        struct_list = services.credentials.List(
            query=f"user_id:{user_id}",
            offset=0,
            limit=100,
            db=self._db,
        ).call()

        # update user
        user = self._db.exec(sqlmodel.select(models.User).where(models.User.user_id == user_id)).one()
        user.credentials_count = struct_list.count
        self._db.commit()

        return 0
