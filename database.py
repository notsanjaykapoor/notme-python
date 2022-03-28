import os

from sqlmodel import create_engine

connect_args = {
  "check_same_thread": False,
}

engine = create_engine(os.environ.get("DATABASE_URL"), echo=False, connect_args=connect_args)
