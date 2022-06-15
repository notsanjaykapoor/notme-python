import sqlmodel

import services.entities.watches


def test_entity_watches_slurp(session: sqlmodel.Session):
    file = "./data/notme/config/entity_watches.toml"

    struct_slurp = services.entities.watches.Slurp(db=session, toml_file=file).call()

    assert struct_slurp.code == 0
    assert struct_slurp.count == 2

    struct_list = services.entities.watches.List(db=session, query="", offset=0, limit=100).call()

    assert struct_list.code == 0
    assert struct_list.count == 2

    # should be idempotent

    struct_slurp = services.entities.watches.Slurp(db=session, toml_file=file).call()

    assert struct_slurp.code == 0
    assert struct_slurp.count == 0
