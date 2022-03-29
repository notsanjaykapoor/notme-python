from dotenv import load_dotenv

load_dotenv() # take environment variables from .env.

from database import engine
from dataclasses import dataclass, field
from fastapi import Depends, FastAPI, HTTPException, WebSocket
from sqlmodel import Session, SQLModel
from typing import List, Optional

import logging

from log import logging_init
from models.user import User
from services.users.get import UserGet
from services.users.create import UserCreate
from services.users.list import UsersList
from services.ws.reader import WsReader

logger = logging_init("console")


app = FastAPI()

# db dependency
def get_db():
  with Session(engine) as session:
    yield session

@app.on_event("startup")
def on_startup():
  logger.info(f"api.startup")

  # create db tables
  SQLModel.metadata.create_all(engine)

@app.on_event("shutdown")
def on_shutdown():
  logger.info(f"api.shutdown")

@app.get("/")
def get_root():
  return {"Hello": "World"}

@app.post("/users", response_model=int)
def user_create(user_id: str):
  logger.info(f"api.user.create")

  struct = UserCreate(user_id).call()

  return struct.user_id

@app.get("/users/{user_id}", response_model=User)
def user_get(user_id: str, db: Session = Depends(get_db)):
  logger.info(f"api.user.get")

  struct = UserGet(db, user_id).call()

  return struct.user

@app.get("/users", response_model=list[User])
def users_list(query: str = "", offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
  logger.info(f"api.users.list")

  struct = UsersList(db, query, offset, limit).call()

  logger.info(f"api.users.list response {struct}")

  return struct.users

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  await websocket.accept()

  try:
    logger.info("api.ws connected")

    await WsReader(websocket).call()
  except Exception as e:
    logger.info(f"api.ws exception {e}")
