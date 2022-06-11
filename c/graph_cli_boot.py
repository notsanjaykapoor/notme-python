#!/usr/bin/env python

from dotenv import load_dotenv

load_dotenv()

import os
import sys
import typer

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import database
import log
import services.entities
import services.graph.commands
import services.graph.driver
import services.graph.stream

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
                struct_list = services.entities.List(
                    db=db, query="", offset=db_offset, limit=db_limit
                ).call()

                if not struct_list.objects:
                    break

                for entity in struct_list.objects:
                    services.graph.stream.Process(
                        db=db, driver=driver, entity=entity
                    ).call()

                db_offset += db_limit

    os.system("./c/graph-cli count")


if __name__ == "__main__":
    app()
