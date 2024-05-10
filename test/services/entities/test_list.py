import test

import pytest
import sqlmodel
import ulid

import services.entities


@pytest.fixture
def entity_id(session: sqlmodel.Session):
    entity_id = ulid.new().str

    entity = test.EntityFactory.build(
        entity_id=entity_id,
        name="test person foo",
    )

    services.entities.Create(db=session, entities=[entity]).call()

    yield entity_id

    services.entities.delete_by_id(db=session, ids=[entity_id])


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


@pytest.mark.skip(reason="sqlalchemy 2.0 upgrade changes to tsvector")
def test_entity_list_with_full_text_search(session: sqlmodel.Session, entity_id: str):
    struct_list = services.entities.List(
        db=session,
        query=f"entity_id:{entity_id} name_text:person",
    ).call()

    assert struct_list.count == 1
    assert struct_list.objects[0].entity_id == entity_id

    struct_list = services.entities.List(
        db=session,
        query=f"entity_id:{entity_id} name_text:(test+|+baz)",
    ).call()

    assert struct_list.count == 1
    assert struct_list.objects[0].entity_id == entity_id

    struct_list = services.entities.List(
        db=session,
        query=f"entity_id:{entity_id} name_text:(test+&+!baz)",
    ).call()

    assert struct_list.count == 1
    assert struct_list.objects[0].entity_id == entity_id

    struct_list = services.entities.List(
        db=session,
        query=f"entity_id:{entity_id} name_text:(test+&+baz)",
    ).call()

    assert struct_list.count == 0
