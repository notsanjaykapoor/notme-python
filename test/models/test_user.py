import os
import pytest

import services

from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from main_api import app, get_db
from models.user import User


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


def test_user(session: Session):  #
    print(f"test_user")

    # def get_session_override():
    #     return session  #

    # app.dependency_overrides[get_db] = get_session_override

    struct_create = services.users.UserCreate(db=session, user_id="user-id").call()

    assert struct_create.code == 0

    # print(f"user created {struct_create.user_id}")

    struct_list = services.users.UsersList(db=session, query="").call()

    # print(f"users list {struct_list.users}")

    assert len(struct_list.users) == 1
