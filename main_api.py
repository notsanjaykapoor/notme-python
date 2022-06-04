from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import contextvars
import logging
import strawberry
import sys
import ulid

import gql
import services.users

from database import engine
from dataclasses import dataclass, field
from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket
from sqlmodel import Session, SQLModel
from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig

from context import request_id
from log import logging_init
from models.user import User


logger = logging_init("api")

# api db dependency
def get_db():
    with Session(engine) as session:
        yield session


# gql db dependency
async def get_gql_context(db=Depends(get_db)):
    return {"db": db}


# initialize graphql schema and router

gql_schema = strawberry.Schema(
    query=gql.Query,
    config=StrawberryConfig(auto_camel_case=False),
)

graphql_router = GraphQLRouter(
    gql_schema,
    context_getter=get_gql_context,
)

app = FastAPI()

app.include_router(graphql_router, prefix="/graphql")


@app.on_event("startup")
def on_startup():
    logger.info(f"api.startup")

    # create db tables
    SQLModel.metadata.create_all(engine)


@app.on_event("shutdown")
def on_shutdown():
    logger.info(f"api.shutdown")


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    # set request id context var
    request_id.set(ulid.new().str)
    response = await call_next(request)
    return response


@app.get("/ping")
def api_ping():
    return {
        "code": 0,
        "message": "pong",
    }


@app.post("/users", response_model=int)
def user_create(user_id: str):
    logger.info(f"{request_id.get()} api.user.create")

    struct = services.users.Create(user_id).call()

    return struct.user_id


@app.get("/users/{user_id}", response_model=User)
def user_get(user_id: str, db: Session = Depends(get_db)):
    logger.info(f"{request_id.get()} api.user.get")

    struct = services.users.Get(db, user_id).call()

    return struct.user


@app.get("/users", response_model=list[User])
def users_list(
    query: str = "", offset: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    logger.info(f"{request_id.get()} api.users.list")

    struct = services.users.List(db, query, offset, limit).call()

    # logger.info(f"api.users.list response {struct}")

    return struct.users
