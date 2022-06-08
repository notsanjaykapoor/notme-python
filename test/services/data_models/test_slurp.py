import pytest

import random
import ulid

from sqlmodel import Session

import services.data_models
import services.graph.connections


def test_data_models_slurp(session: Session):
    file = "./data/slurp/data_models.toml"

    struct_slurp = services.data_models.Slurp(db=session, toml_file=file).call()

    assert struct_slurp.code == 0
    assert struct_slurp.created == 11

    struct_list = services.data_models.List(
        db=session, query="", offset=0, limit=100
    ).call()

    assert struct_list.code == 0
    assert struct_list.objects_count == 11

    # build graph connections

    struct_build = services.graph.connections.Build(db=session).call()

    assert struct_build.code == 0
    assert struct_build.created == 11
