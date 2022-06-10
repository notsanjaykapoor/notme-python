import pytest

from sqlmodel import Session

import services.data_models


def test_data_models_slurp(session: Session):
    file = "./data/slurp/data_models.toml"

    struct_slurp = services.data_models.Slurp(db=session, toml_file=file).call()

    assert struct_slurp.code == 0
    assert struct_slurp.created == 13

    struct_list = services.data_models.List(
        db=session, query="", offset=0, limit=100
    ).call()

    assert struct_list.code == 0
    assert struct_list.count == 13

    # should be idempotent

    struct_slurp = services.data_models.Slurp(db=session, toml_file=file).call()

    assert struct_slurp.code == 0
    assert struct_slurp.created == 0
