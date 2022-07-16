#!/usr/bin/env python

from dotenv import load_dotenv

load_dotenv()

import os  # noqa: E402
import sys  # noqa: E402

import typer  # noqa: E402

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import log  # noqa: E402
import services.database.session  # noqa: E402
import services.entities  # noqa: E402
import services.entity_locations  # noqa: E402
import services.graph.commands  # noqa: E402
import services.graph.session  # noqa: E402
import services.graph.sync  # noqa: E402

logger = log.init("cli")

app = typer.Typer()

# initialize database
services.database.session.migrate()


@app.command()
def geo():
    """sync geo data to graph database"""

    sync_entity_locations()

    os.system("./c/graph-cli count")


@app.command()
def reset():
    """truncate graph database, sync db to graph database"""

    with services.graph.session.get() as session:
        services.graph.commands.truncate(session)

    logger.info("[graph-cli] truncated")

    sync_entities()
    sync_entity_locations()

    os.system("./c/graph-cli count")


def sync_entities():
    with services.database.session.get() as db, services.graph.session.get() as neo:
        struct_list = services.entities.ListIds(db=db).call()

        for entity_id in struct_list.ids:
            services.graph.sync.Entity(db=db, neo=neo, entity_id=entity_id).call()


def sync_entity_locations(offset: int = 0, limit: int = 1024):
    with services.database.session.get() as db, services.graph.session.get() as neo:
        # find all entity location objects
        struct_list = services.entity_locations.List(db=db, query="", offset=offset, limit=limit).call()

        for entity_location in struct_list.objects:
            services.graph.sync.EntityGeo(db=db, neo=neo, entity_location=entity_location).call()


if __name__ == "__main__":
    app()
