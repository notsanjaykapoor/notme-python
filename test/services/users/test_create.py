import sqlmodel

import services.users


def test_user_create(session: sqlmodel.Session):  #
    struct_create = services.users.Create(db=session, user_id="user-1").call()
    assert struct_create.code == 0

    struct_list = services.users.List(db=session, query="").call()
    assert struct_list.count == 1
