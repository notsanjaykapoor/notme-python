import random

import ulid
from sqlmodel import Session

import services.entities


def test_entity_create(session: Session):
    entity_id = ulid.new().str

    entity_params = [
        {
            "entity_id": entity_id,
            "entity_name": "person",
            "name": "person 1",
            "slug": "first_name",
            "type_name": "string",
            "type_value": random.sample(["First", None], 1)[0],
        },
        {
            "entity_id": entity_id,
            "entity_name": "person",
            "name": "person 2",
            "slug": "last_name",
            "type_name": "string",
            "type_value": random.sample(["Last", None], 1)[0],
        },
    ]

    struct_create = services.entities.Create(
        db=session,
        objects=entity_params,
    ).call()

    assert struct_create.code == 0
    assert len(struct_create.ids) == 2
    assert struct_create.count == 2
