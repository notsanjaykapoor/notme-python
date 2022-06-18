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
import services.graph.sync  # noqa: E402

logger = log.logging_init("cli")

app = typer.Typer()

# initialize database
database.migrate()


@app.command()
def geo():
    """sync geo data to graph database"""

    sync_geo()

    os.system("./c/graph-cli count")


@app.command()
def reset():
    """truncate graph database, sync db to graph database"""

    services.graph.commands.truncate()
    logger.info("[graph-cli] truncated")

    sync_entities()
    sync_geo()

    os.system("./c/graph-cli count")


def sync_entities():
    with database.session() as db:
        with services.graph.driver.get() as driver:
            db_offset = 0
            db_limit = 100

            while True:
                struct_list = services.entities.List(db=db, query="", offset=db_offset, limit=db_limit).call()

                if not struct_list.objects:
                    break

                for entity in struct_list.objects:
                    services.graph.sync.Entity(db=db, driver=driver, entity_id=entity.id).call()

                db_offset += db_limit


def sync_geo():
    with database.session() as db:
        with services.graph.driver.get() as driver:
            # find all geo entities

            query = "slug:lat"
            struct_list = services.entities.List(db=db, query=query, offset=0, limit=1000).call()

            for entity in struct_list.objects:
                services.graph.sync.EntityGeo(db=db, driver=driver, entity_id=entity.entity_id).call()


if __name__ == "__main__":
    app()
