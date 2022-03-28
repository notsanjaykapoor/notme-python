from dataclasses import dataclass
from sqlmodel import select, Session

from sqlmodel.sql.expression import Select, SelectOfScalar
SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

from models.user import User
from services.mql.parse import Parse

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

class List:
  def __init__(self, db: Session, query: str = "", offset: int = 0, limit: int=20):
    self.db = db
    self.query = query
    self.offset = offset
    self.limit = limit

  def call(self):
    struct = Struct(0, [], [])

    # parse query
    print(f"users list {self.query}")

    struct_tokens = Parse(self.query).call()

    print(f"users list tokens {struct_tokens.tokens}")

    # initialize default query

    query_db = select(User)

    for token in struct_tokens.tokens:
      value = token["value"]

      if token["field"] == "user_id":
        query_db = query_db.where(User.user_id == value)

    struct.users = self.db.exec(query_db.offset(self.offset).limit(self.limit)).all()

    return struct
