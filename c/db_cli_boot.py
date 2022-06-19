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
import services.db  # noqa: E402
import services.entities  # noqa: E402
import services.entities.watches  # noqa: E402
import services.graph.commands  # noqa: E402
import services.kafka.topics  # noqa: E402

logger = log.init("cli")

app = typer.Typer()

# initialize database
database.migrate()


@app.command()
def reset(
    data_file: str = typer.Option(..., "--file", "-f", help="toml data file"),
    config_path: str = typer.Option("./data/notme/config", "--config-path", help="config path"),
):
    _db_truncate()
    _db_sync(data_file=data_file, config_path=config_path)

    os.system("./c/graph-cli sync geo")


@app.command()
def sync(
    data_file: str = typer.Option(..., "--file", "-f", help="toml data file"),
    config_path: str = typer.Option("./data/notme/config", "--config-path", help="config path"),
):
    _db_sync(data_file=data_file, config_path=config_path)

    os.system("./c/graph-cli sync geo")


def _db_sync(data_file: str, config_path: str):
    with sqlmodel.Session(database.engine) as db:
        # db config
        struct_models = services.data_models.Slurp(db=db, toml_file=f"{config_path}/data_models.toml").call()
        struct_links = services.data_links.Slurp(db=db, toml_file=f"{config_path}/data_links.toml").call()
        struct_watches = services.entities.watches.Slurp(db=db, toml_file=f"{config_path}/entity_watches.toml").call()

        # db entities
        struct_entities = services.entities.Slurp(db=db, json_file=data_file).call()

        struct_watches_match = services.entities.watches.Match(db=db, entity_ids=struct_entities.ids, topic="source").call()

        # publish 'entity.changed' messages
        services.entities.watches.PublishChanged(
            watches=struct_watches_match.watches,
            entity_ids=struct_entities.ids,
        ).call()

        # publish 'entity.geo.changed' messages for each unique entity
        services.entities.watches.PublishGeoChanged(
            watches=struct_watches_match.watches,
            entity_ids=list(struct_entities.entity_ids),
        ).call()

        logger.info(f"[db-cli] imported data models {struct_models.count}")
        logger.info(f"[db-cli] imported data links {struct_links.count}")
        logger.info(f"[db-cli] imported entity watches {struct_watches.count}")
        logger.info(f"[db-cli] imported entities {struct_entities.count}")


def _db_truncate():
    with sqlmodel.Session(database.engine) as db:
        services.graph.commands.truncate()

        services.db.truncate_table(db=db, table_name="entities")
        services.db.truncate_table(db=db, table_name="entity_watches")
        services.db.truncate_table(db=db, table_name="data_links")
        services.db.truncate_table(db=db, table_name="data_models")

        logger.info("[db-cli] db and graph truncated")


if __name__ == "__main__":
    app()
