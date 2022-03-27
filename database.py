from sqlmodel import create_engine, SQLModel

DATABASE_URL = "sqlite:///./sqlite_dev.db"

connect_args = {
  "check_same_thread": False,
  }

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)
