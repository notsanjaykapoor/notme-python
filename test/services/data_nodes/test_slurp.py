import sqlmodel

import services.data_nodes


def test_data_nodes_slurp(session: sqlmodel.Session):
    file = "./data/notme/config/data_nodes.toml"

    struct_slurp = services.data_nodes.Slurp(db=session, toml_file=file).call()

    assert struct_slurp.code == 0
    assert struct_slurp.count == 3

    struct_list = services.data_nodes.List(db=session, query="", offset=0, limit=100).call()

    assert struct_list.code == 0
    assert struct_list.count == 3

    # should be idempotent

    struct_slurp = services.data_nodes.Slurp(db=session, toml_file=file).call()

    assert struct_slurp.code == 0
    assert struct_slurp.count == 0
