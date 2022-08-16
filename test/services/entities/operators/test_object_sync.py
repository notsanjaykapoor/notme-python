import json

import pytest
import sqlmodel

import services.data_models
import services.entities
import services.entities.operators
import services.entity_locations


@pytest.fixture()
def data_models(session: sqlmodel.Session):
    """create base data models used to validate data links"""
    data_file = "./test/data/data_models/data_model_person.json"
    objects = json.load(open(data_file))

    struct_create = services.data_models.Create(
        db=session,
        objects=objects,
    ).call()

    yield struct_create.ids

    services.data_models.delete_by_id(db=session, ids=struct_create.ids)


def test_sync_basic(session: sqlmodel.Session, data_models: list[int]):
    data_file = "./test/data/entities/entities__basic.json"

    objects = json.load(open(data_file))

    entity_ids = []

    for object in objects:
        struct_entities = services.entities.operators.ObjectSync(db=session, object=object).call()

        assert struct_entities.code == 201
        assert len(struct_entities.ids) == 3
        assert len(struct_entities.location_ids) == 0

        entity_ids += struct_entities.ids

    for object in objects:
        # should mark as duplicate
        struct_entities = services.entities.operators.ObjectSync(db=session, object=object).call()

        assert struct_entities.code == 409
        assert len(struct_entities.ids) == 3

    services.entities.delete_by_id(db=session, ids=entity_ids)  # type: ignore


def test_sync_basic_geo(session: sqlmodel.Session, data_models: list[int]):
    data_file = "./test/data/entities/entities__basic_geo.json"

    objects = json.load(open(data_file))

    entity_ids = []
    entity_location_ids = []

    for object in objects:
        struct_entities = services.entities.operators.ObjectSync(db=session, object=object).call()

        assert struct_entities.code == 201
        assert len(struct_entities.ids) == 5
        assert len(struct_entities.location_ids) == 1

        entity_ids += struct_entities.ids
        entity_location_ids += struct_entities.location_ids

    services.entities.delete_by_id(db=session, ids=entity_ids)  # type: ignore
    services.entity_locations.delete_by_id(db=session, ids=entity_location_ids)  # type: ignore


def test_sync_basic_update(session: sqlmodel.Session, data_models: list[int]):
    data_file = "./test/data/entities/entities__basic.json"

    objects = json.load(open(data_file))

    entity_ids = []
    entity_location_ids = []

    for object in objects:
        struct_entities = services.entities.operators.ObjectSync(db=session, object=object).call()

        assert struct_entities.code == 201
        assert len(struct_entities.ids) == 3
        assert len(struct_entities.location_ids) == 0

        entity_ids += struct_entities.ids

    # sync existing entity with changes

    data_file = "./test/data/entities/entities__basic_update.json"

    objects = json.load(open(data_file))

    for object in objects:
        struct_entities = services.entities.operators.ObjectSync(db=session, object=object).call()

        assert struct_entities.code == 200
        assert len(struct_entities.ids) == 5
        assert len(struct_entities.location_ids) == 1

        entity_ids += struct_entities.ids
        entity_location_ids += struct_entities.location_ids

    # should mark original version as replaced

    struct_list = services.entities.List(
        db=session,
        query="state:replaced",
    ).call()

    assert struct_list.code == 0
    assert struct_list.count == 3

    struct_list = services.entities.List(
        db=session,
        query="state:active",
    ).call()

    assert struct_list.code == 0
    assert struct_list.count == 5

    # try sync again, should return 409 this time

    for object in objects:
        struct_entities = services.entities.operators.ObjectSync(db=session, object=object).call()

        assert struct_entities.code == 409
        assert len(struct_entities.ids) == 5
        assert len(struct_entities.location_ids) == 0

    services.entities.delete_by_id(db=session, ids=entity_ids)  # type: ignore
    services.entity_locations.delete_by_id(db=session, ids=entity_location_ids)  # type: ignore
