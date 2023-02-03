import os
import typing

import datadog
import sqlmodel
import strawberry
import ulid
from fastapi import APIRouter, Depends, FastAPI, Request  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# from sqlmodel import Session  # noqa: E402
from strawberry.fastapi import GraphQLRouter  # noqa: E402
from strawberry.schema.config import StrawberryConfig  # noqa: E402

import context  # noqa: E402
import dot_init  # noqa: F401
import gql  # noqa: E402
import log  # noqa: E402
import models  # noqa: E402
import services.database.session  # noqa: E402
import services.entities  # noqa: E402
import services.openid
import services.users  # noqa: E402
import services.webauthn.auth
import services.webauthn.register

logger = log.init("api")

# create app object
app = FastAPI()


# db dependency
def get_db():
    with services.database.session.get() as session:
        yield session


# gql db dependency
async def get_gql_context(db=Depends(get_db)):
    return {"db": db}


api_router = APIRouter(
    prefix="/api/v1",
    tags=["api"],
    dependencies=[Depends(get_db)],
    responses={404: {"description": "Not found"}},
)

# initialize graphql schema and router

gql_schema = strawberry.Schema(
    query=gql.Query,
    config=StrawberryConfig(auto_camel_case=False),
)

graphql_router = GraphQLRouter(
    gql_schema,
    context_getter=get_gql_context,
)

app.include_router(graphql_router, prefix="/graphql")
app.include_router(api_router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware, secret_key=os.environ.get("FASTAPI_SESSION_KEY"), max_age=None
)


@app.on_event("startup")
def on_startup():
    logger.info("api.startup")

    services.database.session.migrate()


@app.on_event("shutdown")
def on_shutdown():
    logger.info("api.shutdown")


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    # set request id context var
    context.rid_set(ulid.new().str)
    response = await call_next(request)
    return response


@datadog.statsd.timed("api.v1.entities.list", tags=["env:dev", "api:rest"])
@app.get("/api/v1/entities", tags=["entities"], response_model=list[models.Entity])
def entities_list(
    query: str = "",
    offset: int = 0,
    limit: int = 100,
    db: sqlmodel.Session = Depends(get_db),
):
    logger.info(f"{context.rid_get()} api.v1.entities.list")

    struct = services.entities.List(db, query, offset, limit).call()

    # logger.info(f"api.users.list response {struct}")

    return struct.objects


# kubernetes inspired health probes
@app.get("/health")
@app.get("/health/live")
@app.get("/health/ready")
@app.get("/health/startup")
def api_health():
    return {
        "api": "up",
    }


@datadog.statsd.timed("api.ping", tags=["env:dev", "api:rest"])
@app.get("/ping")
def api_ping():
    return {
        "code": 0,
        "message": "pong",
    }


@app.get("/openid/auth")
def openid_login(
    db: sqlmodel.Session = Depends(get_db),
    email: typing.Optional[str] = "",
    idp: typing.Optional[str] = "",
):
    logger.info(f"{context.rid_get()} openid.auth")

    if email:
        # map email to idp
        struct_list = services.users.List(
            db=db, query=f"email:{email}", offset=0, limit=1
        ).call()

        if struct_list.code != 0:
            return {"code": 409, "errors": ["user not found"]}

        idp = struct_list.objects[0].idp

    if not idp:
        return {"code": 422, "errors": ["idp is required"]}

    # map idp to auth uri

    struct_auth = services.openid.AuthUriGet(idp=idp).call()

    if struct_auth.code != 0:
        return {"code": struct_auth.code, "errors": struct_auth.errors}

    return {"code": 0, "uri": struct_auth.uri, "idp": idp}


@app.get("/openid/authentik/callback")
def openid_authentik_callback(request: Request, state: str, code: str):
    logger.info(f"{context.rid_get()} openid.authentik.callback try")

    struct_auth = services.openid.AuthCallback(
        idp="authentik", code=code, state=state
    ).call()

    if struct_auth.code == 0:
        request.session["user_jwt"] = struct_auth.token
        request.session["user_email"] = struct_auth.email

    logger.info(f"{context.rid_get()} openid.authentik.callback completed")

    return {
        "code": struct_auth.code,
        "errors": struct_auth.errors,
    }


@app.get("/openid/google/callback")
def openid_google_callback(request: Request, state: str, code: str):
    logger.info(f"{context.rid_get()} openid.google.callback try")

    struct_auth = services.openid.AuthCallback(
        idp="google", code=code, state=state
    ).call()

    logger.info(f"{context.rid_get()} openid.google.callback completed")

    return {
        "code": struct_auth.code,
        "errors": struct_auth.errors,
    }


@datadog.statsd.timed("api.users.create", tags=["env:dev", "api:rest"])
@app.post("/api/v1/users", response_model=int)
def user_create(user_id: str, db: sqlmodel.Session = Depends(get_db)):
    logger.info(f"{context.rid_get()} api.users.create")

    struct = services.users.Create(db, user_id, params={}).call()

    return struct.id


@datadog.statsd.timed("api.users.get", tags=["env:dev"])
@app.get("/api/v1/users/{user_id}", response_model=models.User)
def user_get(user_id: str, db: sqlmodel.Session = Depends(get_db)):
    logger.info(f"{context.rid_get()} api.users.get")

    struct = services.users.Get(db, user_id).call()

    return struct.user


@datadog.statsd.timed("api.users.list", tags=["env:dev"])
@app.get("/api/v1/users", response_model=list[models.User])
def users_list(
    query: str = "",
    offset: int = 0,
    limit: int = 100,
    db: sqlmodel.Session = Depends(get_db),
):
    logger.info(f"{context.rid_get()} api.users.list")

    struct = services.users.List(db, query, offset, limit).call()

    # logger.info(f"api.users.list response {struct}")

    return struct.objects


@datadog.statsd.timed("api.webauthn.auth.complete", tags=["env:dev", "api:rest"])
@app.post("/api/v1/webauthn/auth/complete")
def webauthn_auth_complete(
    params: services.webauthn.auth.CompleteParams,
    db: sqlmodel.Session = Depends(get_db),
):
    logger.info(f"{context.rid_get()} api.webauthn.auth.complete")

    struct = services.webauthn.auth.Complete(params, db).call()

    return {"code": struct.code, "object": {}}


@datadog.statsd.timed("api.webauthn.auth.init", tags=["env:dev", "api:rest"])
@app.post("/api/v1/webauthn/auth/init")
def webauthn_auth_init(
    params: services.webauthn.auth.InitParams, db: sqlmodel.Session = Depends(get_db)
):
    logger.info(f"{context.rid_get()} api.webauthn.auth.init")

    struct = services.webauthn.auth.Init(params, db).call()

    logger.info(f"{context.rid_get()} response {type(struct.object)}")

    return {"code": struct.code, "object": struct.object}


@datadog.statsd.timed("api.webauthn.register.complete", tags=["env:dev", "api:rest"])
@app.post("/api/v1/webauthn/register/complete")
def webauthn_register_complete(
    params: services.webauthn.register.CompleteParams,
    db: sqlmodel.Session = Depends(get_db),
):
    logger.info(f"{context.rid_get()} api.webauthn.register.complete")

    struct = services.webauthn.register.Complete(params, db).call()

    return {"code": struct.code, "object": {}}


@datadog.statsd.timed("api.webauthn.register.init", tags=["env:dev", "api:rest"])
@app.post("/api/v1/webauthn/register/init")
def webauthn_register_init(
    params: services.webauthn.register.InitParams,
    db: sqlmodel.Session = Depends(get_db),
):
    logger.info(f"{context.rid_get()} api.webauthn.register.init")

    struct = services.webauthn.register.Init(params, db).call()

    logger.info(f"{context.rid_get()} response {type(struct.object)}")

    return {"code": struct.code, "object": struct.object}
