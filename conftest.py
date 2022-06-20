import os

import neo4j
import pytest
import sqlmodel
import sqlmodel.pool


@pytest.fixture(name="session")  #
def session_fixture():  #
    test_db_name = os.environ.get("DATABASE_TEST_URL")

    # print(f"session_fixture db {test_db_name}")

    engine = sqlmodel.create_engine(
        test_db_name,
        connect_args={"check_same_thread": False},
        poolclass=sqlmodel.pool.StaticPool,
    )

    sqlmodel.SQLModel.metadata.create_all(engine)

    with sqlmodel.Session(engine) as session:
        yield session  #

    sqlmodel.SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="neo_session")
def neo_session_fixture():
    driver = neo4j.GraphDatabase.driver(
        os.environ["NEO4J_BOLT_URL"],
        auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]),
    )

    session = driver.session(database=os.environ["NEO4J_DB_NAME"])  # todo

    yield session
