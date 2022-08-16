import os
import sys
import time

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import typer  # noqa: E402

import dot_init  # noqa: E402, F401
import log  # noqa: E402
import services.boot  # noqa: E402
import services.database  # noqa: E402
import services.entities.input  # noqa: E402
import services.entities.operators  # noqa: E402
import services.timely.flows  # noqa: E402

logger = log.init("cli")

app = typer.Typer()


@app.command()
def csv(file="./data/notme/cdr/data_sessions_1.csv"):
    with services.database.session.get() as db, services.graph.session.get() as neo:
        services.boot.reset(db=db, neo=neo)

    time_start = time.monotonic()

    services.timely.flows.CdrDsImport(
        input=services.entities.input.stream_csv(file),
    ).call()

    logger.info(f"{__name__} duration {time.monotonic() - time_start} seconds")


@app.command()
def excel(file="./data/notme/cdr/data_sessions_1.xlsx"):
    services.boot.reset()

    time_start = time.monotonic()

    services.timely.flows.CdrDsImport(
        input=services.entities.input.stream_xls(file),
    ).call()

    logger.info(f"{__name__} duration {time.monotonic() - time_start} seconds")


if __name__ == "__main__":
    app()
