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
import services.database.session  # noqa: E402
import services.entities.input  # noqa: E402
import services.entities.operators  # noqa: E402
import services.graph.session  # noqa: E402
import services.timely.flows  # noqa: E402
import services.timely.inputs  # noqa: E402

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


@app.command()  # original version
def file():
    with services.database.session.get() as db, services.graph.session.get() as neo:
        services.boot.reset(db=db, neo=neo)

    time_start = time.monotonic()

    services.timely.flows.EntityImport(
        input=services.entities.input.stream_json(file=file_path),
    ).call()

    logger.info(f"{__name__} duration {time.monotonic() - time_start} seconds")


@app.command()  # new version
def json():
    with services.database.session.get() as db, services.graph.session.get() as neo:
        services.boot.reset(db=db, neo=neo)

        time_start = time.monotonic()

        struct_data_mappings = services.data_mappings.List(
            db=db,
            query="",
            offset=0,
            limit=1024,
        ).call()

        struct_data_models = services.data_models.List(
            db=db,
            query="",
            offset=0,
            limit=1024,
        ).call()

        struct_json_input = services.timely.flows.StreamJson(
            input=services.timely.inputs.input_json(file=file_path),
            data_mappings=struct_data_mappings.objects,
            data_models=struct_data_models.objects,
        ).call()

        struct_db_sync = services.timely.flows.EntityDbSync(
            input=struct_json_input.output,
            db=db,
        ).call()

        struct_graph_sync = services.timely.flows.EntityGraphSync(
            input=struct_db_sync.output,
            db=db,
            neo=neo,
        ).call()

        time_end = time.monotonic()

        for epoch, item in struct_graph_sync.output:
            print(f"{__name__} graph sync epoch {epoch} item {item}")

    logger.info(f"{__name__} duration {time_end - time_start} seconds")


@app.command()
def random(count: int = typer.Option(..., "--count")):
    with services.database.session.get() as db, services.graph.session.get() as neo:
        services.boot.reset(db=db, neo=neo)

        time_start = time.monotonic()

        services.timely.flows.EntityImport(
            input=services.entities.input.stream_random(records=count),
        ).call()

        time_end = time.monotonic()

    logger.info(f"{__name__} duration {time_end - time_start} seconds")


@app.command()
def random_new(count: int = typer.Option(..., "--count")):
    with services.database.session.get() as db, services.graph.session.get() as neo:
        services.boot.reset(db=db, neo=neo)

        time_start = time.monotonic()

        struct_data_mappings = services.data_mappings.List(
            db=db,
            query="",
            offset=0,
            limit=1024,
        ).call()

        struct_data_models = services.data_models.List(
            db=db,
            query="",
            offset=0,
            limit=1024,
        ).call()

        # services.timely.flows.EntityImport(
        #     input=services.entities.input.stream_random(records=count),
        # ).call()

        struct_json_input = services.timely.flows.StreamJson(
            input=services.entities.input.stream_random(records=count),
            data_mappings=struct_data_mappings.objects,
            data_models=struct_data_models.objects,
        ).call()

        struct_db_sync = services.timely.flows.EntityDbSync(
            input=struct_json_input.output,
            db=db,
        ).call()

        struct_graph_sync = services.timely.flows.EntityGraphSync(
            input=struct_db_sync.output,
            db=db,
            neo=neo,
        ).call()

        time_end = time.monotonic()

        for epoch, item in struct_graph_sync.output:
            print(f"{__name__} graph sync epoch {epoch} item {item}")

    logger.info(f"{__name__} duration {time_end - time_start} seconds")


if __name__ == "__main__":
    app()
