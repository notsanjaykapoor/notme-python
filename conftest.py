import os
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
