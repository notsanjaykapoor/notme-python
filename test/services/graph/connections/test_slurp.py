import pytest

import random
import ulid

from sqlmodel import Session

import services.graph


def test_graph_connections_slurp(session: Session):
    file = "./data/graph/connections.toml"

    struct_slurp = services.graph.connections.Slurp(db=session, toml_file=file).call()

    assert struct_slurp.code == 0
    assert struct_slurp.created == 11
    assert struct_slurp.exists == 0

    struct_slurp = services.graph.connections.Slurp(db=session, toml_file=file).call()

    assert struct_slurp.code == 0
    assert struct_slurp.created == 0
    assert struct_slurp.exists == 11
