import logging

from dataclasses import dataclass
from sqlmodel import select, Session
from typing import Optional

from models.user import User

@dataclass
class Struct:
  code: int
  user_id: int
  errors: list[str]

class UserCreate:
  def __init__(self, db: Session, user_id: str):
    self._db = db
    self._user_id = user_id
    self._logger = logging.getLogger("api")

  def call(self):
    struct = Struct(0, None, [])

    self._logger.info(f"{__name__} user_id {self._user_id}")

    db_object = User(user_id=self._user_id)

    self._db.add(db_object)
    self._db.commit()

    struct.user_id = db_object.id

    return struct
