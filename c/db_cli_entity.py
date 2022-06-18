#!/usr/bin/env python

import os
import sys

import dotenv

sys.path.insert(1, os.path.join(sys.path[0], ".."))

dotenv.load_dotenv()

import sqlalchemy  # noqa: E402
import sqlmodel  # noqa: E402
import typer  # noqa: E402

import database  # noqa: E402
import dog  # noqa: E402
import log  # noqa: E402
import models  # noqa: E402
import services.entities  # noqa: E402

logger = log.init("cli")

# initialize database
database.migrate()

# initialize datadog
dog.init()

app = typer.Typer()


@app.command("count")
def count():
    with database.session() as db:
        count = db.exec(sqlmodel.select([sqlalchemy.func.count(models.Entity.id)])).one()

    logger.info(f"[db-cli] entity_count {count}")


@app.command("list")
def list(query: str = typer.Option("", "--query", "-q")):
    with database.session() as db:
        struct_list = services.entities.List(db, query, 0, 1000).call()

        logger.info(f"[db-cli] entity_list {struct_list.count}")

        for entity in struct_list.objects:
            logger.info(f"[db-cli] {entity.pack()}")
