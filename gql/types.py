import typing

import strawberry


@strawberry.type
class GqlEntity:
    id: int
    entity_id: str
    entity_key: str
    entity_name: str
    name: str
    node: int
    slug: str
    type_name: str
    type_value: str


@strawberry.type
class GqlEntitiesList:
    code: int
    errors: list[str]
    objects: list[GqlEntity]


@strawberry.type
class GqlUser:
    id: int
    user_id: str


@strawberry.type
class GqlUserGet:
    code: int
    errors: list[str]
    user: typing.Optional[GqlUser]


@strawberry.type
class GqlUsersList:
    code: int
    errors: list[str]
    objects: list[GqlUser]
