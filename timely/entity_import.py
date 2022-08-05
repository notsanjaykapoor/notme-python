import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import bytewax  # # noqa: E402
import bytewax.inputs  # # noqa: E402

import dot_init  # noqa: E402, F401
import log  # noqa: E402
import services.database.session  # noqa: E402
import services.entities.operators  # noqa: E402
import services.timely.flows  # noqa: E402

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
            if epoch < resume_epoch:
                continue

            yield bytewax.inputs.AdvanceTo(epoch)
            yield bytewax.inputs.Emit(line)


# test
def output_builder(worker_index, worker_count):
    def output_handler(epoch_item):
        epoch, item = epoch_item
        # print(epoch, json.dumps(key), json.dumps(payload))
        return epoch_item

    return output_handler


services.timely.flows.EntityImport(file=file_path).call()
