#!/usr/bin/env python

from dotenv import load_dotenv

load_dotenv()

import os  # noqa: E402
import sys  # noqa: E402

import typer  # noqa: E402

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import database  # noqa: E402
import log  # noqa: E402
import services.entities  # noqa: E402
import services.graph.commands  # noqa: E402
import services.graph.driver  # noqa: E402
import services.graph.stream  # noqa: E402

logger = log.logging_init("cli")

app = typer.Typer()

# initialize database
database.migrate()


@app.command()
def call(truncate: bool = typer.Option(...)):
    """create graph database"""
    if truncate:
        services.graph.commands.truncate()
        logger.info(f"[graph-cli] truncated")

    with database.session() as db:
        with services.graph.driver.get() as driver:
            db_offset = 0
            db_limit = 1000

            while True:
                struct_list = services.entities.List(db=db, query="", offset=db_offset, limit=db_limit).call()

                if not struct_list.objects:
                    break

                for entity in struct_list.objects:
                    services.graph.stream.Process(db=db, driver=driver, entity=entity).call()

                db_offset += db_limit

    os.system("./c/graph-cli count")


if __name__ == "__main__":
    app()
