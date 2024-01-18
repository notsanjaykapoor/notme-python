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


def test_flow_json(
    session: sqlmodel.Session,
    neo_session: neo4j.Session,
    data_models: list[int],
    data_mappings: list[int],
):
    json_file = "./test/data/entities/entities__basic.json"

    struct_data_mappings = services.data_mappings.List(
        db=session,
        query="",
        offset=0,
        limit=1024,
    ).call()

    struct_data_models = services.data_models.List(
        db=session,
        query="",
        offset=0,
        limit=1024,
    ).call()

    struct_csv_input_output = []

    # set input params using a function (required by bytewax)
    services.timely.inputs.input_json_params(file=json_file)

    _struct_json_input = services.timely.flows.stream_json(
        input=bytewax.inputs.ManualInputConfig(
            services.timely.inputs.input_json_generator
        ),
        output=bytewax.outputs.TestingOutputConfig(struct_csv_input_output),
        data_mappings=struct_data_mappings.objects,
        data_models=struct_data_models.objects,
    )

    for item in struct_csv_input_output:
        print(f"{__name__} flow 1 item {item}")

    # struct_flow_db_sync = services.timely.flows.EntityDbSync(
    #     input=struct_json_input.output,
    #     db=session,
    # ).call()

    # for epoch, item in struct_flow_db_sync.output:
    #     print(f"{__name__} flow 2 epoch {epoch} item {item}")

    # if services.graph.status_up(neo=neo_session) != 0:
    #     return

    # struct_flow_graph_sync = services.timely.flows.EntityGraphSync(
    #     input=struct_flow_db_sync.output,
    #     db=session,
    #     neo=neo_session,
    # ).call()

    # for epoch, item in struct_flow_graph_sync.output:
    #     print(f"{__name__} flow 3 epoch {epoch} item {item}")

    services.database.truncate_table(db=session, table_name="entities")
