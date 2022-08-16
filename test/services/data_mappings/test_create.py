import json

import pytest
import sqlmodel

import services.data_mappings
import services.data_models


@pytest.fixture()
def data_models(session: sqlmodel.Session):
    """create base data models used to validate data mappings"""
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

    yield struct_create.ids

    services.data_models.delete_by_id(db=session, ids=struct_create.ids)


def test_data_mappings_create__valid(session: sqlmodel.Session, data_models: list[int]):
    data_file = "./test/data/data_mappings/data_mapping_user.json"
    objects = json.load(open(data_file))

    struct_create = services.data_mappings.Create(
        db=session,
        objects=objects,
    ).call()

    assert struct_create.code == 0
    assert struct_create.count == 1

    struct_list = services.data_mappings.List(db=session, query="", offset=0, limit=1024).call()

    assert len(struct_list.objects) == 1

    services.data_mappings.delete_by_id(db=session, ids=struct_create.ids)
