#!/usr/bin/env python
import json
import os
import sys

import dotenv
import sqlmodel
import typer

sys.path.insert(1, os.path.join(sys.path[0], ".."))

dotenv.load_dotenv()

import database  # noqa: E402
import log  # noqa: E402
import services.data_links  # noqa: E402
import services.data_models  # noqa: E402
import services.data_nodes  # noqa: E402
import services.db  # noqa: E402
import services.entities  # noqa: E402
import services.graph.commands  # noqa: E402

logger = log.init("cli")

app = typer.Typer()

# initialize database
database.migrate()


@app.command()
def call(
    json_file: str = typer.Option(..., "--file", "-f", help="json data file"),
    truncate: bool = typer.Option(...),
    path: str = typer.Option("./data/slurp", "--path", "-p", help="config path"),
):
    objects = json.load(open(json_file))

    with sqlmodel.Session(database.engine) as db:
        if truncate:
            services.graph.commands.truncate()

            services.db.truncate_table(db=db, table_name="entities")

            services.db.truncate_table(db=db, table_name="data_links")
            services.db.truncate_table(db=db, table_name="data_nodes")
            services.db.truncate_table(db=db, table_name="data_models")

            logger.info("[db-cli] db and graph truncated")

        struct_models = services.data_models.Slurp(db=db, toml_file=f"{path}/data_models.toml").call()

        struct_nodes = services.data_nodes.Slurp(db=db, toml_file=f"{path}/data_nodes.toml").call()

        struct_links = services.data_links.Slurp(db=db, toml_file=f"{path}/data_links.toml").call()

        struct_entity_slurp = services.entities.Slurp(db=db, objects=objects).call()

        logger.info(f"[db-cli] imported data config, models {struct_models.created} nodes {struct_nodes.created} links {struct_links.created}")

        logger.info(f"[db-cli] entities imported {struct_entity_slurp.count}")


if __name__ == "__main__":
    app()
