import strawberry
import typing

from database import engine
from sqlmodel import Session, SQLModel

from gql import types
from log import logging_init
from services.users.get import UserGet
from services.users.list import UsersList

logger = logging_init("gql")

@strawberry.type
class GqlQuery:
  @strawberry.field
  def user_get(self, user_id: str) -> types.GqlUserGet:
    logger.info(f"gql.user_get {user_id}")

    with Session(engine) as db_session:
      return UserGet(db_session, user_id).call()

  @strawberry.field
  def users_list(self, query: str="", offset: int=0, limit: int=10) -> types.GqlUsersList:
    logger.info(f"gql.users_list query {query}")

    with Session(engine) as db_session:
      return UsersList(db_session, query, offset, limit).call()
