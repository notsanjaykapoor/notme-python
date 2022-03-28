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
from services.crypto.pkey.create import Create as PkeyCreate
from services.crypto.pkey.sign import Sign as PkeySign
from services.crypto.pkey.verify import Verify as PkeyVerify
from services.users.create import Create as UserCreate
from services.users.get import Get as UserGet
from services.users.list import List as UsersList

logging_init()

logger = logging.getLogger("console")

app = typer.Typer()

@app.command()
def crypto_sign(data: str = "secret"):
  struct_pkey = PkeyCreate().call()

  private_key = struct_pkey.key

  struct_sign = PkeySign(
    private_key,
    data
  ).call()

  logger.info(f"cli sign {struct_sign}")

  public_key = private_key.public_key()
  signature = struct_sign.encoded

  struct_verify = PkeyVerify(
    public_key,
    data,
    signature,
  ).call()

  logger.info(f"cli verify {struct_verify}")

@app.command()
def topic_read(topic: str, group: str="python"):
  # create reader with generic handler
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
