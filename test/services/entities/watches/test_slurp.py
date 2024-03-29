import sqlmodel

import services.entity_watches


def test_entity_watches_slurp(session: sqlmodel.Session):
    file = "./data/notme/config/entity_watches.toml"

    struct_slurp = services.entity_watches.Slurp(db=session, toml_file=file).call()

    assert struct_slurp.code == 0
    assert struct_slurp.count == 3

    struct_list = services.entity_watches.List(db=session, query="", offset=0, limit=100).call()

    assert struct_list.code == 0
    assert struct_list.count == 3

    # should be idempotent

    struct_slurp = services.entity_watches.Slurp(db=session, toml_file=file).call()

    assert struct_slurp.code == 0
    assert struct_slurp.count == 0
