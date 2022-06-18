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
import models  # noqa: E402
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

        # publish 'entity.changed' messages for each entity
        for entity_id in struct_entities.ids:
            message = models.Entity.message_changed_cls(int(entity_id))

            services.entities.Publish(message=message, topic=services.kafka.topics.TOPIC_GRAPH_SYNC).call()

        # publish 'entity.geo.changed' messages for each unique entity
        struct_ids = services.entities.ListIds(db=db).call()

        for entity_geo_id in struct_ids.ids:
            message = models.Entity.message_geo_changed_cls(entity_geo_id)

            services.entities.Publish(message=message, topic=services.kafka.topics.TOPIC_GRAPH_SYNC).call()

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
