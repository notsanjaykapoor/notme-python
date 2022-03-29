from dataclasses import dataclass
from sqlmodel import select, Session
from typing import Optional
import logging

from models.user import User

@dataclass
class Struct:
  code: int
  user_id: int
  errors: list[str]

class UserCreate:
  def __init__(self, db: Session, user_id: str):
    self.db = db
    self.user_id = user_id
    self.logger = logging.getLogger("service")

  def call(self):
    struct = Struct(0, None, [])

    self.logger.info(f"{__name__} user_id {self.user_id}")

    db_object = User(user_id=self.user_id)

    self.db.add(db_object)
    self.db.commit()

    struct.user_id = db_object.id

    return struct
