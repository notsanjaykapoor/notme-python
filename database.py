import os

from sqlmodel import SQLModel, create_engine

connect_args = {
    "check_same_thread": False,
}

engine = create_engine(
    os.environ.get("DATABASE_URL"), echo=False, connect_args=connect_args
)

# create/migrate db tables
def migrate(engine):
    SQLModel.metadata.create_all(engine)
