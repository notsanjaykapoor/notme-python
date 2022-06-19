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
import services.graph.driver  # noqa: E402
import services.graph.query  # noqa: E402

logger = log.logging_init("cli")

app = typer.Typer()


@app.command()
def create():
    """create graph indicies"""

    with database.session() as db:
        services.entities.ListEntityNames(db).call()

    # for name in struct_list.values:
    #     # create graph constraint on id property
    #     query = f"create index {name}_id_index IF NOT EXISTS FOR (n:{name}) on (n:id)"

    #     logger.info(f"[graph-cli] {query}")

    #     _records = services.graph.query.execute(query, {})


@app.command()
def show():
    """show all graph indexes"""
    query = "show all index"

    records = services.graph.query.execute(query, {})

    for record in records:
        logger.info(f"[graph-cli] {record}")
