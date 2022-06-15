#!/usr/bin/env python
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
import services.entities.watches  # noqa: E402
import services.graph.commands  # noqa: E402

logger = log.init("cli")

app = typer.Typer()

# initialize database
database.migrate()


@app.command()
def reset(
    data_file: str = typer.Option(..., "--file", "-f", help="toml data file"),
    config_path: str = typer.Option("./data/notme/config", "--config-path", help="config path"),
):
    with sqlmodel.Session(database.engine) as db:
        services.graph.commands.truncate()

        services.db.truncate_table(db=db, table_name="entities")
        services.db.truncate_table(db=db, table_name="data_links")
        services.db.truncate_table(db=db, table_name="data_nodes")
        services.db.truncate_table(db=db, table_name="data_models")

        logger.info("[db-cli] db and graph truncated")

    slurp(data_file=data_file, config_path=config_path)


@app.command()
def sync(
    data_file: str = typer.Option(..., "--file", "-f", help="toml data file"),
    config_path: str = typer.Option("./data/notme/config", "--config-path", help="config path"),
):
    slurp(data_file=data_file, config_path=config_path)


def slurp(data_file: str, config_path: str):
    with sqlmodel.Session(database.engine) as db:
        struct_models = services.data_models.Slurp(db=db, toml_file=f"{config_path}/data_models.toml").call()

        struct_nodes = services.data_nodes.Slurp(db=db, toml_file=f"{config_path}/data_nodes.toml").call()

        struct_links = services.data_links.Slurp(db=db, toml_file=f"{config_path}/data_links.toml").call()

        struct_watches = services.entities.watches.Slurp(db=db, toml_file=f"{config_path}/entity_watches.toml").call()

        struct_entities = services.entities.Slurp(db=db, json_file=data_file).call()

        logger.info(f"[db-cli] imported data models {struct_models.count}")
        logger.info(f"[db-cli] imported data nodes {struct_nodes.count}")
        logger.info(f"[db-cli] imported data links {struct_links.count}")
        logger.info(f"[db-cli] imported entity watches {struct_watches.count}")
        logger.info(f"[db-cli] imported entities {struct_entities.count}")


if __name__ == "__main__":
    app()
