import strawberry
from strawberry.types import Info

import gql.types
import log
import services.entities
import services.users

logger = log.init("gql")


@strawberry.type
class Query:
    @strawberry.field
    def user_get(self, user_id: str, info: Info) -> gql.types.GqlUserGet:
        logger.info(f"gql.{info.field_name} {user_id}")

        return services.users.Get(info.context["db"], user_id).call()  # type: ignore

    @strawberry.field
    def users_list(self, info: Info, query: str = "", offset: int = 0, limit: int = 10) -> gql.types.GqlUsersList:
        logger.info(f"gql.{info.field_name} query {query}")

        return services.users.List(info.context["db"], query, offset, limit).call()  # type: ignore

    @strawberry.field
    def entities_list(self, info: Info, query: str = "", offset: int = 0, limit: int = 10) -> gql.types.GqlEntitiesList:
        logger.info(f"gql.{info.field_name} query {query}")

        return services.entities.List(info.context["db"], query, offset, limit).call()  # type: ignore
