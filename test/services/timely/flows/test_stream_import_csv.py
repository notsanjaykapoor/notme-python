import json

import bytewax.inputs
import bytewax.outputs
import neo4j
import pytest
import sqlmodel

import services.data_mappings
import services.data_models
import services.database
import services.entities
import services.entities.operators
import services.entity_locations
import services.graph
import services.timely.flows
import services.timely.inputs


@pytest.fixture()
def data_mappings(session: sqlmodel.Session):
    """create data mappings for user object to person model"""
    data_file = "./test/data/data_mappings/data_mapping_user.json"
    objects = json.load(open(data_file))

    struct_create = services.data_mappings.Create(
        db=session,
        objects=objects,
    ).call()

    yield struct_create.ids

    services.data_mappings.delete_by_id(db=session, ids=struct_create.ids)


@pytest.fixture()
def data_models(session: sqlmodel.Session):
    """create base data models used to validate data links"""
    data_model_file = "./test/data/data_models/data_model_person.json"
    objects = json.load(open(data_model_file))

    struct_create = services.data_models.Create(
        db=session,
        objects=objects,
    ).call()

    yield struct_create.ids

    services.data_models.delete_by_id(db=session, ids=struct_create.ids)


def test_flow_csv_user(session: sqlmodel.Session, neo_session: neo4j.Session, data_models: list[int], data_mappings: list[int]):
    csv_file = "./test/data/data_streams/user_1.csv"

    struct_data_mappings = services.data_mappings.List(
        db=session,
        query=f"id:{data_mappings[0]}",
        offset=0,
        limit=1,
    ).call()

    assert len(struct_data_mappings.objects) == 1

    data_mapping_user = struct_data_mappings.objects[0]

    # data_model maps user to person
    assert data_mapping_user.model_name == "person"
    assert data_mapping_user.obj_name == "user"

    struct_data_models = services.data_models.List(
        db=session,
        query=f"obj_name:{data_mapping_user.model_name}",
        offset=0,
        limit=1024,
    ).call()

    assert len(struct_data_models.objects) == 7

    data_models_person = struct_data_models.objects

    struct_csv_input_output = []

    # set input params using a function (required by bytewax)
    services.timely.inputs.input_csv_params(file=csv_file)

    struct_csv_input = services.timely.flows.StreamCsv(
        input=bytewax.inputs.ManualInputConfig(services.timely.inputs.input_csv_generator),
        output=bytewax.outputs.TestingOutputConfig(struct_csv_input_output),
        data_mapping=data_mapping_user,
        data_models=data_models_person,
    ).call()

    for item in struct_csv_input_output:
        print(f"{__name__} flow 1 item {item}")

    # struct_db_sync = services.timely.flows.EntityDbSync(
    #     input=struct_csv_input.output,
    #     db=session,
    # ).call()

    # for epoch, item in struct_db_sync.output:
    #     print(f"{__name__} flow 2 epoch {epoch} item {item}")

    # _ = services.entities.List(
    #     db=session,
    #     query="",
    #     offset=0,
    #     limit=1024,
    # ).call()

    # if services.graph.status_up(neo=neo_session) != 0:
    #     return

    # # assert len(struct_entities.objects) == 15

    # struct_graph_sync = services.timely.flows.EntityGraphSync(
    #     input=struct_db_sync.output,
    #     db=session,
    #     neo=neo_session,
    # ).call()

    # for epoch, item in struct_graph_sync.output:
    #     print(f"{__name__} flow 3 epoch {epoch} item {item}")

    services.database.truncate_table(db=session, table_name="entities")


def test_flow_csv_user_random(session: sqlmodel.Session, neo_session: neo4j.Session, data_models: list[int], data_mappings: list[int]):
    csv_file = "./test/data/data_streams/user_random_1.csv"

    struct_data_mappings = services.data_mappings.List(
        db=session,
        query="",
        offset=0,
        limit=1024,
    ).call()

    assert len(struct_data_mappings.objects) == 1

    data_mapping_user = struct_data_mappings.objects[0]

    struct_data_models = services.data_models.List(
        db=session,
        query="",
        offset=0,
        limit=1024,
    ).call()

    assert len(struct_data_models.objects) == 7

    data_models_person = struct_data_models.objects

    struct_csv_input_output = []

    # set input params using a function (required by bytewax)
    services.timely.inputs.input_csv_random_params(file=csv_file, count=5)

    struct_csv_input = services.timely.flows.StreamCsv(
        input=bytewax.inputs.ManualInputConfig(services.timely.inputs.input_csv_random_generator),
        output=bytewax.outputs.TestingOutputConfig(struct_csv_input_output),
        data_mapping=data_mapping_user,
        data_models=data_models_person,
    ).call()

    for item in struct_csv_input_output:
        print(f"{__name__} flow 1 item {item}")

    # struct_db_sync = services.timely.flows.EntityDbSync(
    #     input=struct_csv_input.output,
    #     db=session,
    # ).call()

    # for epoch, item in struct_db_sync.output:
    #     print(f"{__name__} flow 2 epoch {epoch} item {item}")

    # _ = services.entities.List(
    #     db=session,
    #     query="",
    #     offset=0,
    #     limit=1024,
    # ).call()

    # if services.graph.status_up(neo=neo_session) != 0:
    #     return

    # struct_graph_sync = services.timely.flows.EntityGraphSync(
    #     input=struct_db_sync.output,
    #     db=session,
    #     neo=neo_session,
    # ).call()

    # for epoch, item in struct_graph_sync.output:
    #     print(f"{__name__} flow 3 epoch {epoch} item {item}")

    services.database.truncate_table(db=session, table_name="entities")
