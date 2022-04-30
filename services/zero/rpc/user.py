import logging
import ulid

from database import engine
from dataclasses import dataclass, field
from sqlmodel import Session, SQLModel

from context import request_id

from services.users.get import UserGet
from services.users.list import UsersList

class ZeroRpcUser:
  def __init__(self) -> None:
    self._logger = logging.getLogger("service")

  def user_get(self, user_id: str) -> dict:
    request_id.set(ulid.new().str)

    self._logger.info(f"{request_id.get()} rpc user_get {user_id}")

    with Session(engine) as db:
      struct_get = UserGet(db, user_id).call()

      response = {"code": struct_get.code}

      if struct_get.code == 0:
        response |= struct_get.user.pack()

      return response

  def users_list(self, query: str, offset: int = 0, limit: int = 20) -> dict:
    request_id.set(ulid.new().str)

    self._logger.info(f"{request_id.get()} rpc users_list {query}")

    with Session(engine) as db:
      struct_list = UsersList(db, query, offset, limit).call()

      response = {"code": struct_list.code, "count": len(struct_list.users)}

      return response
