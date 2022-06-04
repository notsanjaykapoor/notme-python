import os
import pytest

from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool


@pytest.fixture(name="session")  #
def session_fixture():  #
    test_db_name = os.environ.get("DATABASE_TEST_URL")

    # print(f"session_fixture db {test_db_name}")

    engine = create_engine(
        test_db_name, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session  #

    SQLModel.metadata.drop_all(engine)
