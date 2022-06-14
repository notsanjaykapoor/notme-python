import pytest
import sqlmodel

import services.data_links
import services.data_nodes


@pytest.fixture()
def data_nodes(session: sqlmodel.Session):
    """create base data nodes used to validate data links"""
    objects = [
        {
            "src_name": "case",
            "src_slug": "jacket_id",
        },
        {
            "src_name": "person",
            "src_slug": "record_id",
        },
    ]

    struct_create = services.data_nodes.Create(
        db=session,
        objects=objects,
    ).call()

    yield struct_create.object_ids


def test_data_link_create(session: sqlmodel.Session, data_nodes: list[int]):
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


def test_data_link_create__with_invalid_slug_name_eq(session: sqlmodel.Session, data_nodes: list[int]):
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


def test_data_link_create__with_missing_data_node(session: sqlmodel.Session, data_nodes: list[int]):
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
