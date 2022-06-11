import os
import sqlalchemy
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


@sqlalchemy.event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # print("sqlachemy connect event")
    cursor = dbapi_connection.cursor()
    cursor.execute("pragma journal_mode=wal")
    cursor.close()
