import strawberry
import typing

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
  users: list[GqlUser]