import random

import pytest
import sqlmodel
import ulid

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
            "object_node": 0,
            "object_slug": "last_name",
            "object_type": "string",
        },
        {
            "object_name": "person",
            "object_node": 0,
            "object_slug": "lat",
            "object_type": "string",
        },
        {
            "object_name": "person",
            "object_node": 0,
            "object_slug": "lon",
            "object_type": "string",
        },
    ]

    struct_create = services.data_models.Create(
        db=session,
        objects=objects,
    ).call()

    yield struct_create.object_ids


def test_entity_create(session: sqlmodel.Session, data_models: list[int]):
    entity_id = ulid.new().str

    entity_params = [
        {
            "entity_id": entity_id,
            "entity_name": "person",
            "name": "person 1",
            "slug": "first_name",
            "tags": "|person|",
            "type_name": "string",
            "type_value": random.sample(["First", None], 1)[0],
        },
        {
            "entity_id": entity_id,
            "entity_name": "person",
            "name": "person 1",
            "slug": "last_name",
            "tags": "|random|",
            "type_name": "string",
            "type_value": random.sample(["Last", None], 1)[0],
        },
    ]

    struct_dms = services.data_models.Hash(db=session, query="").call()

    struct_create = services.entities.Create(
        db=session,
        objects=entity_params,
        data_models=struct_dms.object,
    ).call()

    assert struct_create.code == 0
    assert struct_create.count == 2
    assert struct_create.entity_count == 1
    assert struct_create.location_count == 0

    services.entities.List(db=session, query="", offset=0, limit=100).call()


def test_entity_create_with_geo(session: sqlmodel.Session, data_models: list[int]):
    entity_id = ulid.new().str

    entity_params = [
        {
            "entity_id": entity_id,
            "entity_name": "person",
            "name": "person 1",
            "slug": "lat",
            "type_name": "string",
            "type_value": "41.88094",
        },
        {
            "entity_id": entity_id,
            "entity_name": "person",
            "name": "person 1",
            "slug": "lon",
            "type_name": "string",
            "type_value": "-87.63004",
        },
    ]

    struct_dms = services.data_models.Hash(db=session, query="").call()

    struct_create = services.entities.Create(
        db=session,
        objects=entity_params,
        data_models=struct_dms.object,
    ).call()

    assert struct_create.code == 0
    assert struct_create.count == 2
    assert struct_create.entity_count == 1
    assert struct_create.location_count == 1

    services.entities.List(db=session, query="", offset=0, limit=100).call()
