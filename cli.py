from dotenv import load_dotenv

load_dotenv() # take environment variables from .env.

import typer
from typing import Optional

from sqlmodel import Session, SQLModel
from database import engine

import logging

from log import logging_init
from kafka.handlers.generic import Generic
from kafka.reader import Reader
from kafka.writer import Writer
from models import user
from services.users.create import Create as UserCreate
from services.users.get import Get as UserGet
from services.users.list import List as UsersList

logging_init()

logger = logging.getLogger("console")

app = typer.Typer()

@app.command()
def topic_read(topic: str, group: str="python"):
  handler = Generic()

  writer = Reader(topic, group, handler)
  writer.call()

@app.command()
def topic_write(topic: str):
  writer = Writer(topic, {"message": "ping"})
  writer.call()

@app.command()
def user_create(name: str):
  logger.info(f"cli user {name} create try")

  with Session(engine) as session:
    user = UserGet(session, name).call()

    if user:
      log.info(f"cli result user {name} exists")
      return 0

    user_id = UserCreate(session, name).call()

    log.info(f"cli result user {name} created")

    return user_id

@app.command()
def user_search(query: Optional[str] = ""):
  with Session(engine) as session:
    service = UsersList(session, query, 0, 10)
    struct = service.call()

    for user in struct.users:
      logger.info(f"cli result {user}")

if __name__ == "__main__":
  app()
