import logging

import sqlmodel
import ulid
from database import engine

import services.users
from context import request_id


class User:
    def __init__(self) -> None:
        self._logger = logging.getLogger("service")

    def user_get(self, user_id: str) -> dict:
        request_id.set(ulid.new().str)

        self._logger.info(f"{request_id.get()} rpc user_get {user_id}")

        with sqlmodel.Session(engine) as db:
            struct_get = services.users.Get(db, user_id).call()

            response = {"code": struct_get.code}

            if struct_get.user:
                response |= struct_get.user.pack()

            return response

    def users_list(self, query: str, offset: int = 0, limit: int = 20) -> dict:
        request_id.set(ulid.new().str)

        self._logger.info(f"{request_id.get()} rpc users_list {query}")

        with sqlmodel.Session(engine) as db:
            struct_list = services.users.List(db, query, offset, limit).call()

            response = {"code": struct_list.code, "count": len(struct_list.objects)}

            return response
