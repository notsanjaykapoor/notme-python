import os

import sqlmodel

connect_args = {
    "check_same_thread": False,
}

engine = sqlmodel.create_engine(
    os.environ.get("DATABASE_URL"), echo=False, connect_args=connect_args
)

# create/migrate db tables
def migrate():
    sqlmodel.SQLModel.metadata.create_all(engine)


# get session object
def session():
    return sqlmodel.Session(engine)
