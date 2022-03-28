from dotenv import load_dotenv

load_dotenv() # take environment variables from .env.

from database import engine
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, SQLModel
from typing import List, Optional

import logging

from log import logging_init
from models import user
from services.users.get import Get as UserGet
from services.users.create import Create as UserCreate
from services.users.list import List as UsersList

logging_init()

logger = logging.getLogger("console")

app = FastAPI()

# db dependency
def get_db():
  with Session(engine) as session:
    yield session

@app.on_event("startup")
def on_startup():
  # create db tables
  SQLModel.metadata.create_all(engine)

@app.get("/")
def read_root():
  return {"Hello": "World"}

@app.post("/users", response_model=int)
def user_create(user_id: str):
  logger.info(f"api.user.create")

  service = UserCreate(user_id)
  return service.call()

@app.get("/users/{user_id}", response_model=user.User)
def user_get(user_id: str, db: Session = Depends(get_db)):
  logger.info(f"api.user.get")

  service = UserGet(db, user_id)
  return service.call()

@app.get("/users", response_model=list[user.User])
def users_list(query: str = "", offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
  logger.info(f"api.users.list")

  service = UsersList(db, query, offset, limit)
  struct = service.call()

  return struct.users
