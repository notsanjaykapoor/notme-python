import pytest
import sqlmodel

import services.users


@pytest.fixture
def user_id(session: sqlmodel.Session):
    struct_create = services.users.Create(db=session, user_id="user-1").call()
    assert struct_create.code == 0
    assert struct_create.id

    yield struct_create.id

    services.users.delete_by_id(db=session, ids=[struct_create.id])


def test_user_list(session: sqlmodel.Session, user_id: int):  #
    struct_list = services.users.List(db=session, query="user_id:~user").call()
    assert struct_list.count == 1

    struct_list = services.users.List(db=session, query="user_id:~xxx").call()
    assert struct_list.count == 0
