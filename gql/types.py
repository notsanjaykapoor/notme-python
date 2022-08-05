import typing

import strawberry


@strawberry.type
class GqlBlock:
    id: int
    timestamp_unix: int
    tx_id: str
    user_id: str
    vote: str


@strawberry.type
class GqlBlocksList:
    code: int
    errors: list[str]
    blocks: list[GqlBlock]  # todo


@strawberry.type
class GqlDoc:
    clock: str
    data: str
    doc_id: str
    id: int
    name: str
    user_id: str


@strawberry.type
class GqlDocsList:
    code: int
    errors: list[str]
    docs: list[GqlDoc]  # todo


@strawberry.type
class GqlEntity:
    id: int
    entity_id: str
    entity_key: str
    entity_name: str
    name: str
    node: int
    slug: str
    state: str
    type_name: str
    type_value: str


@strawberry.type
class GqlEntitiesList:
    code: int
    errors: list[str]
    objects: list[GqlEntity]


@strawberry.type
class GqlNode:
    eid: str  # entity object id
    labels: list[str]
    lat: float
    lon: float
    name: str
    nid: str  # neo4j graph id


@strawberry.type
class GqlEdge:
    name: str
    src_nid: str
    tgt_nid: str


@strawberry.type
class GqlNodesList:
    code: int
    errors: list[str]
    node_start: typing.Optional[GqlNode]
    node_end: typing.Optional[GqlNode]
    nodes: list[GqlNode]
    nodes_count: int
    edges: list[GqlEdge]
    edges_count: int


@strawberry.type
class GqlSecret:
    id: int
    login: str
    origin: str
    user_id: str


@strawberry.type
class GqlSecretsList:
    code: int
    errors: list[str]
    secrets: list[GqlSecret]  # todo


@strawberry.type
class GqlUser:
    id: int
    credentials_count: int
    emails_count: int
    mobile: typing.Optional[str]
    mobile_count: int
    state: str
    totp_count: int
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
