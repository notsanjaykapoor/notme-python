import pytest
import sqlmodel
import ulid

import services.entities


@pytest.fixture()
def entity_id(session: sqlmodel.Session):
    entity_id = ulid.new().str

    entity_params = {
        "entity_id": entity_id,
        "entity_name": "person",
        "slug": "first_name",
        "type_name": "string",
        "type_value": "First",
    }

    services.entities.Create(
        db=session,
        entity_objects=[entity_params],
    ).call()

    yield entity_id


def test_entity_list(session: sqlmodel.Session, entity_id: str):
    # query with exact value
    struct_list = services.entities.List(
        db=session,
        query=f"entity_id:{entity_id}",
    ).call()

    assert struct_list.count == 1
    assert struct_list.objects[0].entity_id == entity_id

    # query with or value
    struct_list = services.entities.List(
        db=session,
        query=f"entity_id:{entity_id}|{ulid.new().str}",
    ).call()

    assert struct_list.count == 1
    assert struct_list.objects[0].entity_id == entity_id

    # query with non-existing value
    struct_list = services.entities.List(
        db=session,
        query="entity_id:~xxx",
    ).call()

    assert struct_list.count == 0
