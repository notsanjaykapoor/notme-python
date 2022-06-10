#!/usr/bin/env python

from dotenv import load_dotenv

load_dotenv()

import json
import os
import sys
import typer

from sqlalchemy import func
from sqlmodel import select, Session, SQLModel

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from log import logging_init

import database
import models
import services.data_links
import services.data_models
import services.data_nodes
import services.db
import services.entities
import services.graph.commands

logger = logging_init("cli")

app = typer.Typer()

# initialize database
database.migrate(database.engine)


# db dependency
def get_db():
    with Session(database.engine) as session:
        yield session


@app.command()
def data_config_slurp(
    path: str = "./data/slurp",
    truncate: bool = typer.Option(...),
):
    with Session(database.engine) as db:
        if truncate:
            services.db.truncate_table(db=db, table_name="data_links")
            services.db.truncate_table(db=db, table_name="data_nodes")
            services.db.truncate_table(db=db, table_name="data_models")

            logger.info(f"[db-cli] data config truncated")

        struct_models = services.data_models.Slurp(
            db=db, toml_file=f"{path}/data_models.toml"
        ).call()

        struct_nodes = services.data_nodes.Slurp(
            db=db, toml_file=f"{path}/data_nodes.toml"
        ).call()

        struct_links = services.data_links.Slurp(
            db=db, toml_file=f"{path}/data_links.toml"
        ).call()

        logger.info(
            f"[db-cli] imported data config, models {struct_models.created} nodes {struct_nodes.created} links {struct_links.created}"
        )


@app.command()
def entity_count():
    with Session(database.engine) as db:
        count = db.exec(select([func.count(models.Entity.id)])).one()

    logger.info(f"[db-cli] entity_count {count}")


@app.command()
def entity_slurp(
    file: str = typer.Option(...),
    truncate: bool = typer.Option(...),
):
    objects = json.load(open(file))

    logger.info(f"[db-cli] file {file} objects {len(objects)} truncate {truncate}")

    with Session(database.engine) as db:
        if truncate:
            services.db.truncate_table(db=db, table_name="entities")
            logger.info(f"[db-cli] entities truncated")

            services.graph.commands.truncate()
            logger.info(f"[db-cli] graph truncated")

        struct = services.entities.Slurp(db=db, objects=objects).call()
        logger.info(f"[db-cli] imported {struct.count}")


if __name__ == "__main__":
    app()
