import os

import neo4j
import pytest
import sqlalchemy
import sqlmodel
import sqlmodel.pool

import dot_init  # noqa: F401
import models


@pytest.fixture(name="session")
def session_fixture():
    test_db_name = os.environ.get("DATABASE_TEST_URL")

    connect_args = {}

    if "sqlite" in test_db_name:
        # sqlite specific
        connect_args = {"check_same_thread": False}

    # print(f"session_fixture db {test_db_name}")

    engine = sqlmodel.create_engine(
        test_db_name,
        connect_args=connect_args,
        poolclass=sqlmodel.pool.StaticPool,
    )

    sqlmodel.SQLModel.metadata.create_all(engine)

    # sqlalchemy tables
    if not sqlalchemy.inspect(engine).has_table(models.EntityLocation.__tablename__):
        models.EntityLocation.__table__.create(engine)

    with sqlmodel.Session(engine) as session:
        yield session

    # sqlalchemy tables
    if sqlalchemy.inspect(engine).has_table(models.EntityLocation.__tablename__):
        models.EntityLocation.__table__.drop(engine)

    sqlmodel.SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="neo_session")
def neo_session_fixture():
    driver = neo4j.GraphDatabase.driver(
        os.environ["NEO4J_BOLT_URL"],
        auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]),
    )

    # todo: setup test database
    session = driver.session(database=os.environ["NEO4J_DB_TEST_NAME"])

    yield session
