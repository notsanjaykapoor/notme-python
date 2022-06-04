import strawberry
import typing

from database import engine
from sqlmodel import Session, SQLModel
from strawberry.types import Info

import services.users

from gql import types
from log import logging_init

logger = logging_init("gql")


@strawberry.type
class GqlQuery:
    @strawberry.field
    def user_get(self, user_id: str, info: Info) -> types.GqlUserGet:
        logger.info(f"gql.{info.field_name} {user_id}")

        return services.users.Get(info.context["db"], user_id).call()

    @strawberry.field
    def users_list(
        self, info: Info, query: str = "", offset: int = 0, limit: int = 10
    ) -> types.GqlUsersList:
        logger.info(f"gql.{info.field_name} query {query}")

        return services.users.List(info.context["db"], query, offset, limit).call()
