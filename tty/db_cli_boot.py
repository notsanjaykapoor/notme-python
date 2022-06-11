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

import database
import log
import models
import services.data_links
import services.data_models
import services.data_nodes
import services.db
import services.entities
import services.graph.commands

logger = log.init("cli")

app = typer.Typer()

# initialize database
database.migrate()


# db dependency
def get_db():
    with database.session() as session:
        yield session


@app.command()
def call(
    json_file: str = typer.Option(..., "--file", "-f", help="json data file"),
    truncate: bool = typer.Option(...),
    path: str = typer.Option("./data/slurp", "--path", "-p", help="config path"),
):
    objects = json.load(open(json_file))

    with Session(database.engine) as db:
        if truncate:
            services.graph.commands.truncate()

            services.db.truncate_table(db=db, table_name="entities")

            services.db.truncate_table(db=db, table_name="data_links")
            services.db.truncate_table(db=db, table_name="data_nodes")
            services.db.truncate_table(db=db, table_name="data_models")

            logger.info(f"[db-cli] db and graph truncated")

        struct_models = services.data_models.Slurp(
            db=db, toml_file=f"{path}/data_models.toml"
        ).call()

        struct_nodes = services.data_nodes.Slurp(
            db=db, toml_file=f"{path}/data_nodes.toml"
        ).call()

        struct_links = services.data_links.Slurp(
            db=db, toml_file=f"{path}/data_links.toml"
        ).call()

        struct_entity_slurp = services.entities.Slurp(db=db, objects=objects).call()

        logger.info(
            f"[db-cli] imported data config, models {struct_models.created} nodes {struct_nodes.created} links {struct_links.created}"
        )

        logger.info(f"[db-cli] entities imported {struct_entity_slurp.count}")


if __name__ == "__main__":
    app()