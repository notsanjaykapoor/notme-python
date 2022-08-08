import os
import sys
import time

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import bytewax  # noqa: E402
import bytewax.inputs  # noqa: E402
import typer  # noqa: E402

import dot_init  # noqa: E402, F401
import log  # noqa: E402
import services.boot  # noqa: E402
import services.database  # noqa: E402
import services.entities.input.stream_file  # noqa: E402
import services.entities.input.stream_random  # noqa: E402
import services.entities.operators  # noqa: E402
import services.timely.flows  # noqa: E402

logger = log.init("cli")

app = typer.Typer()

file_path = "./data/notme/entities/entities.json"


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


@app.command()
def file():
    services.boot.reset()

    time_start = time.monotonic()

    services.timely.flows.EntityImport(
        input=services.entities.input.stream_file(file=file_path),
    ).call()

    logger.info(f"{__name__} duration {time.monotonic() - time_start} seconds")


@app.command()
def random(count: int = typer.Option(..., "--count")):
    services.boot.reset()

    time_start = time.monotonic()

    services.timely.flows.EntityImport(
        input=services.entities.input.stream_random(records=count),
    ).call()

    logger.info(f"{__name__} duration {time.monotonic() - time_start} seconds")


if __name__ == "__main__":
    app()
