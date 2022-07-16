import os

import neo4j
import pytest
import sqlalchemy
import sqlalchemy.future
import sqlmodel
import sqlmodel.pool

import dot_init  # noqa: F401
import models

test_db_name = os.environ.get("DATABASE_TEST_URL")
connect_args: dict = {}

assert test_db_name

if "sqlite" in test_db_name:
    # sqlite specific
    connect_args = {"check_same_thread": False}

engine = sqlmodel.create_engine(
    test_db_name,
    connect_args=connect_args,
    poolclass=sqlmodel.pool.StaticPool,
)


def database_tables_create(engine: sqlalchemy.future.Engine):
    sqlmodel.SQLModel.metadata.create_all(engine)

    # sqlalchemy tables

    if not sqlalchemy.inspect(engine).has_table(models.City.__tablename__):
        models.City.__table__.create(engine)

    if not sqlalchemy.inspect(engine).has_table(models.EntityLocation.__tablename__):
        models.EntityLocation.__table__.create(engine)


def database_tables_drop(engine: sqlalchemy.future.Engine):
    # sqlalchemy tables

    if sqlalchemy.inspect(engine).has_table(models.City.__tablename__):
        models.City.__table__.drop(engine)

    if sqlalchemy.inspect(engine).has_table(models.EntityLocation.__tablename__):
        models.EntityLocation.__table__.drop(engine)

    sqlmodel.SQLModel.metadata.drop_all(engine)


def database_tables_init(engine: sqlalchemy.future.Engine):
    # initialize hypertables
    session = sqlmodel.Session(engine)
    session.execute("select create_hypertable('events', 'timestamp')")


# Set up the database once
database_tables_drop(engine)
database_tables_create(engine)
database_tables_init(engine)


@pytest.fixture(name="session")
def session_fixture():
    connection = engine.connect()
    transaction = connection.begin()

    # begin a nested transaction (using SAVEPOINT)
    nested = connection.begin_nested()

    session = sqlmodel.Session(engine)

    # if the application code calls session.commit, it will end the nested transaction
    # when that happens, start a new one.
    @sqlalchemy.event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    # yield session to test
    yield session

    session.close()
    # rollback the overall transaction, restoring the state before the test ran
    transaction.rollback()
    connection.close()


@pytest.fixture(name="neo_session")
def neo_session_fixture():
    driver = neo4j.GraphDatabase.driver(
        os.environ["NEO4J_HOST_URL"],
        auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]),
    )

    # todo: setup test database
    session = driver.session(database=os.environ["NEO4J_DB_TEST_NAME"])

    yield session

    # todo: cleanup
