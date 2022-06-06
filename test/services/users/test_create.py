import pytest

import services.users

from sqlmodel import Session


def test_user_create(session: Session):  #
    # app.dependency_overrides[get_db] = get_session_override

    struct_create = services.users.Create(db=session, user_id="user-1").call()
    assert struct_create.code == 0

    struct_list = services.users.List(db=session, query="").call()
    assert len(struct_list.users) == 1
