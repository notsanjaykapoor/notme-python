import pytest
import sqlmodel

import services.data_links
import services.data_models


@pytest.fixture()
def data_models(session: sqlmodel.Session):
    """create base data models used to validate data links"""
    objects = [
        {
            "object_name": "case",
            "object_node": 1,
            "object_slug": "jacket_id",
            "object_type": "string",
        },
        {
            "object_name": "person",
            "object_node": 1,
            "object_slug": "record_id",
            "object_type": "string",
        },
    ]

    struct_create = services.data_models.Create(
        db=session,
        objects=objects,
    ).call()

    yield struct_create.object_ids


def test_data_link_create(session: sqlmodel.Session, data_models: list[int]):
    objects = [
        {
            "src_name": "case",
            "src_slug": "jacket_id",
            "dst_name": "person",
            "dst_slug": "record_id",
        },
    ]

    struct_create = services.data_links.Create(
        db=session,
        objects=objects,
    ).call()

    assert struct_create.code == 0
    assert struct_create.object_count == 2


def test_data_link_create__with_slug_name_eq(session: sqlmodel.Session, data_models: list[int]):
    objects = [
        {
            "src_name": "case",
            "src_slug": "record_id",
            "dst_name": "person",
            "dst_slug": "record_id",
        },
    ]

    struct_create = services.data_links.Create(
        db=session,
        objects=objects,
    ).call()

    assert struct_create.code == 422
    assert struct_create.object_count == 0


def test_data_link_create__with_object_node_noteq(session: sqlmodel.Session, data_models: list[int]):
    objects = [
        {
            "src_name": "case",
            "src_slug": "jacket_id",
            "dst_name": "person",
            "dst_slug": "bogus_id",
        },
    ]

    struct_create = services.data_links.Create(
        db=session,
        objects=objects,
    ).call()

    assert struct_create.code == 422
    assert struct_create.object_count == 0
