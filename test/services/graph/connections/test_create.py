import pytest

import random
import ulid

from sqlmodel import Session

import services.entities
import services.graph


def test_graph_connections_list(session: Session):
    params = {
        "entity_name": "person",
        "entity_slug": "age",
        "rel_name": "has",
    }

    struct_create = services.graph.connections.Create(db=session, object=params).call()

    assert struct_create.code == 0

    object_id = struct_create.id

    struct_list = services.graph.connections.List(
        db=session, query=f"id:{object_id}"
    ).call()

    assert struct_list.objects_count == 1

    object = struct_list.objects[0]

    assert object.entity_name == "person"
    assert object.entity_slug == "age"
    assert object.rel_name == "has"

    struct_create = services.graph.connections.Create(db=session, object=params).call()

    assert struct_create.code == 409
