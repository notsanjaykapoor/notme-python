from dataclasses import dataclass
from sqlmodel import select, Session

import logging
import re

from sqlmodel.sql.expression import Select, SelectOfScalar
SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

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
  tokens: list[{}]
  errors: list[str]

class UsersList:
  def __init__(self, db: Session, query: str = "", offset: int = 0, limit: int=20):
    self.db = db
    self.query = query
    self.offset = offset
    self.limit = limit

    self.dataset = select(User) # default database query
    self.logger = logging.getLogger("console")

  def call(self):
    struct = Struct(0, [], [])

    self.logger.info(f"{__name__} query {self.query}")

    # tokenize query

    struct_tokens = MqlParse(self.query).call()

    self.logger.info(f"{__name__} tokens {struct_tokens.tokens}")

    for token in struct_tokens.tokens:
      value = token["value"]

      if token["field"] == "user_id":
        match = re.match(r"^~", value)

        if match:
          value_normal = re.sub(r"~", "", value)
          # like query
          self.dataset = self.dataset.where(User.user_id.like('%' + value_normal + '%'))
        else:
          # match query
          self.dataset = self.dataset.where(User.user_id == value)


    struct.users = self.db.exec(self.dataset.offset(self.offset).limit(self.limit)).all()

    return struct
