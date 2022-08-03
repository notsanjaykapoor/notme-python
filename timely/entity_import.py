import json
import os
import sys
import typing

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import bytewax  # # noqa: E402
import bytewax.inputs  # # noqa: E402

import dot_init  # noqa: E402, F401
import log  # noqa: E402
import services.database.session  # noqa: E402
import services.entities.operators  # noqa: E402
import services.graph.operators  # noqa: E402
import services.graph.session  # noqa: E402
import services.graph.sync  # noqa: E402

logger = log.init("cli")

file_path = "./data/notme/entities/entities.json"

# test
def version_last() -> int:
    with services.database.session.get() as db:
        return services.entities.get_max_version(db=db)


# test
def input_builder(worker_index: int, worker_count: int, resume_epoch: int):
    assert worker_index == 0
    assert worker_count == 1

    print(f"resume_epoch {resume_epoch}")

    with open(file_path) as f:
        for epoch, line in enumerate(f):
            # if epoch < resume_epoch:
            #     continue
            yield bytewax.inputs.AdvanceTo(epoch)
            yield bytewax.inputs.Emit(line)


# test
def output_builder(worker_index, worker_count):
    def output_handler(epoch_item):
        epoch, item = epoch_item
        # print(epoch, json.dumps(key), json.dumps(payload))
        return epoch_item

    return output_handler


# input for dataflow
def entity_input(file_name: str) -> typing.Generator[tuple[int, dict], None, None]:
    objects = json.load(open(file_name))
    epoch = 1

    for object in objects:
        yield epoch, object


def entity_sync(object: dict) -> dict:
    with services.database.session.get() as db:
        struct = services.entities.operators.ObjectSync(db=db, object=object).call()
        return {"entity_id": list(struct.entity_ids)[0]}


def graph_geo_sync(object: dict) -> dict:
    with services.database.session.get() as db, services.graph.session.get() as neo:
        struct = services.graph.operators.EntityLocationSync(db=db, neo=neo, entity_id=object["entity_id"]).call()
        object["geo"] = struct.geo
        return object


def graph_object_sync(object: dict) -> dict:
    with services.database.session.get() as db, services.graph.session.get() as neo:
        struct = services.graph.operators.EntitySync(db=db, neo=neo, entity_id=object["entity_id"]).call()
        object["nodes_created"] = struct.nodes_created
        object["edges_created"] = struct.edges_created
        return object


def filter_test(object: dict) -> bool:
    return object["id"] in ["01G5386HVMP79PKM21YJGMFG5K"]


flow_1 = bytewax.Dataflow()
# flow_1.filter(filter_test)
flow_1.map(entity_sync)
# {entity_id: "1XYZABC"}
flow_1.map(graph_object_sync)
# {entity_id: "1XYZABC", "nodes_created": 1, "edges_created": 1}
flow_1.map(graph_geo_sync)
# {entity_id: "1XYZABC", "nodes_created": 1, "edges_created": 1, "geo": 0|1}
flow_1.capture()

flow_2 = bytewax.Dataflow()
flow_2.capture()

# flow_3 = bytewax.Dataflow()
# flow_3.capture()

output_1 = bytewax.run(flow_1, entity_input("./data/notme/entities/entities.json"))

# input_config = bytewax.inputs.ManualInputConfig(input_builder)
# output_1 = bytewax.run_main(flow_1, input_config, output_builder)

for epoch, item in bytewax.run(flow_2, output_1):
    logger.info(f"flow_2 epoch {epoch} item {item}")

# for epoch, item in bytewax.run(flow_3, output_1):
#     print(f"flow_3 epoch {epoch} item {item}")

# for epoch, item in bytewax.run(flow, file_input("./data/notme/entities/entities.json")):
#     print(f"flow_1 epoch {epoch} item {item}")
