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
    """create graph constraints"""

    with database.session() as db:
        struct_list = services.entities.ListEntityNames(db).call()

    for name in struct_list.values:
        # create graph constraint on id property
        query = f"create constraint {name}_id_uniq IF NOT EXISTS FOR (n:{name}) require n.id is unique"

        logger.info(f"[graph-cli] {query}")

        services.graph.query.execute(query, {})


@app.command()
def show():
    """show all graph constraints"""
    query = "show all constraints"

    records = services.graph.query.execute(query, {})

    for record in records:
        logger.info(f"[graph-cli] {record}")
