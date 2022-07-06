import strawberry
from strawberry.types import Info

import context
import dot_init  # noqa: F401
import gql.types
import log
import services.entities
import services.graph.session
import services.nodes
import services.users

logger = log.init("gql")


@strawberry.type
class Query:
    @strawberry.field
    def blocks_list(self, info: Info, query: str = "", offset: int = 0, limit: int = 10) -> gql.types.GqlBlocksList:
        logger.info(f"{context.rid_get()} gql.{info.field_name} query {query}")

        return gql.types.GqlBlocksList(code=0, errors=0, blocks=[])  # type: ignore

    @strawberry.field
    def docs_list(self, info: Info, query: str = "", offset: int = 0, limit: int = 10) -> gql.types.GqlDocsList:
        logger.info(f"{context.rid_get()} gql.{info.field_name} query {query}")

        return gql.types.GqlDocsList(code=0, errors=0, docs=[])  # type: ignore

    @strawberry.field
    def nodes_list(self, info: Info, query: str = "", offset: int = 0, limit: int = 10) -> gql.types.GqlNodesList:
        logger.info(f"{context.rid_get()} gql.{info.field_name} query {query}")

        with services.graph.session.get() as neo:
            return services.nodes.List(
                db=info.context["db"],
                neo=neo,
                query=query,
                offset=offset,
                limit=limit,
            ).call()  # type: ignore

    @strawberry.field
    def entities_list(self, info: Info, query: str = "", offset: int = 0, limit: int = 10) -> gql.types.GqlEntitiesList:
        logger.info(f"{context.rid_get()} gql.{info.field_name} query {query}")

        return services.entities.List(
            db=info.context["db"],
            query=query,
            offset=offset,
            limit=limit,
        ).call()  # type: ignore

    @strawberry.field
    def user_get(self, user_id: str, info: Info) -> gql.types.GqlUserGet:
        logger.info(f"{context.rid_get()} gql.{info.field_name} {user_id}")

        return services.users.Get(db=info.context["db"], user_id=user_id).call()  # type: ignore

    @strawberry.field
    def users_list(self, info: Info, query: str = "", offset: int = 0, limit: int = 10) -> gql.types.GqlUsersList:
        logger.info(f"{context.rid_get()} gql.{info.field_name} query {query}")

        return services.users.List(
            db=info.context["db"],
            query=query,
            offset=offset,
            limit=limit,
        ).call()  # type: ignore
