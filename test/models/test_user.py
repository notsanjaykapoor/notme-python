import pytest

import services.users

from sqlmodel import Session

from main_api import app, get_db


def test_user(session: Session):  #
    print(f"test_user")

    # app.dependency_overrides[get_db] = get_session_override

    struct_create = services.users.Create(db=session, user_id="user-id").call()

    assert struct_create.code == 0

    # print(f"user created {struct_create.user_id}")

    struct_list = services.users.List(db=session, query="").call()

    # print(f"users list {struct_list.users}")

    assert len(struct_list.users) == 1
