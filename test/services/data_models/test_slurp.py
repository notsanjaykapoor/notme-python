import sqlmodel

import services.data_models


def test_data_models_slurp(session: sqlmodel.Session):
    file = "./data/notme/config/data_models.toml"

    struct_slurp = services.data_models.Slurp(db=session, toml_file=file).call()

    assert struct_slurp.code == 0
    assert struct_slurp.count == 32

    slurp_ids = struct_slurp.ids

    struct_list = services.data_models.List(db=session, query="", offset=0, limit=100).call()

    assert struct_list.code == 0
    assert struct_list.count == 32

    # should be idempotent

    struct_slurp = services.data_models.Slurp(db=session, toml_file=file).call()

    assert struct_slurp.code == 0
    assert struct_slurp.count == 0

    services.data_models.delete_by_id(db=session, ids=slurp_ids)
