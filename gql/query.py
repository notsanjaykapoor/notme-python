import strawberry
import typing

from database import engine
from sqlmodel import Session, SQLModel
from strawberry.types import Info

from gql import types
from log import logging_init
from services.users.get import UserGet
from services.users.list import UsersList

logger = logging_init("gql")

@strawberry.type
class GqlQuery:
  @strawberry.field
  def user_get(self, user_id: str, info: Info) -> types.GqlUserGet:
    logger.info(f"gql.{info.field_name} {user_id}")

    return UserGet(info.context["db"], user_id).call()

  @strawberry.field
  def users_list(self, info: Info, query: str="", offset: int=0, limit: int=10) -> types.GqlUsersList:
    logger.info(f"gql.{info.field_name} query {query}")

    return UsersList(info.context["db"], query, offset, limit).call()
