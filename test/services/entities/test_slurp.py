import pytest
import sqlmodel

import services.data_models
import services.entities


@pytest.fixture()
def data_models(session: sqlmodel.Session):
    """create base data models used to validate data links"""
    objects = [
        {
            "object_name": "person",
            "object_node": 0,
            "object_slug": "first_name",
            "object_type": "string",
        },
        {
            "object_name": "person",
            "object_node": 1,
            "object_slug": "id",
            "object_type": "string",
        },
        {
            "object_name": "person",
            "object_node": 0,
            "object_slug": "last_name",
            "object_type": "string",
        },
    ]

    struct_create = services.data_models.Create(
        db=session,
        objects=objects,
    ).call()

    yield struct_create.ids

    services.data_models.delete_by_id(db=session, ids=struct_create.ids)


def test_slurp__without_id(session: sqlmodel.Session, data_models: list[int]):
    data_file = "./test/data/entities_without_id.json"

    # should create missing id field with matching slug
    struct_entities = services.entities.Slurp(db=session, json_file=data_file).call()

    assert struct_entities.code == 0
    assert struct_entities.count == 3

    services.entities.delete_by_id(db=session, ids=struct_entities.ids)  # type: ignore


def test_slurp__without_id_slug(session: sqlmodel.Session, data_models: list[int]):
    data_file = "./test/data/entities_without_id_slug.json"

    # should add missing 'id' slug
    struct_entities = services.entities.Slurp(db=session, json_file=data_file).call()

    assert struct_entities.code == 0
    assert struct_entities.count == 3

    services.entities.delete_by_id(db=session, ids=struct_entities.ids)  # type: ignore


def test_slurp__with_id_invalid(session: sqlmodel.Session, data_models: list[int]):
    data_file = "./test/data/entities_with_id_invalid.json"

    # should add missing 'id' slug
    struct_entities = services.entities.Slurp(db=session, json_file=data_file).call()

    assert struct_entities.code == 422
    assert struct_entities.count == 0

    services.entities.delete_by_id(db=session, ids=struct_entities.ids)  # type: ignore
