import pytest
import ulid

from sqlmodel import Session

import services.entities


@pytest.fixture()
def entity_id(session: Session):
    entity_id = ulid.new().str

    entity_params = {
        "entity_id": entity_id,
        "entity_name": "person",
        "slug": "first_name",
        "type_name": "string",
        "type_value": "First",
    }

    struct_create = services.entities.Create(
        db=session,
        entity_objects=[entity_params],
    ).call()

    yield entity_id


def test_entity_list(session: Session, entity_id: str):
    struct_list = services.entities.List(
        db=session,
        query=f"entity_id:{entity_id}",
    ).call()

    assert len(struct_list.entities) == 1
    assert struct_list.entities[0].entity_id == entity_id

    struct_list = services.entities.List(
        db=session,
        query="entity_id:~xxx",
    ).call()

    assert len(struct_list.entities) == 0
