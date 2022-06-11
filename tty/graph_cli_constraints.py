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
import services.graph
import services.graph.commands
import services.graph.driver
import services.graph.stream

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

        _records = services.graph.query.execute(query, {})


@app.command()
def show():
    """show all graph constraints"""
    query = "show all constraints"

    records = services.graph.query.execute(query, {})

    for record in records:
        logger.info(f"[graph-cli] {record}")
