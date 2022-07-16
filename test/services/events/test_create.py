import sqlmodel

import services.events


def test_event_create(session: sqlmodel.Session):
    object = {
        "name": "entity.created",
        "value": 1.0,
    }

    struct_create = services.events.Create(db=session, object=object).call()
    assert struct_create.code == 0

    struct_list = services.events.List(db=session, query="", offset=0, limit=100).call()
    assert struct_list.code == 0
    assert struct_list.count == 1

    services.events.truncate(db=session)
