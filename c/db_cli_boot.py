#!/usr/bin/env python
import os
import sys

import typer

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import dot_init  # noqa: E402, F401
import log  # noqa: E402
import services.data_links  # noqa: E402
import services.data_models  # noqa: E402
import services.database.session  # noqa: E402
import services.db  # noqa: E402
import services.entities  # noqa: E402
import services.entities.watches  # noqa: E402
import services.graph.commands  # noqa: E402
import services.graph.session  # noqa: E402
import services.kafka.topics  # noqa: E402

logger = log.init("cli")

app = typer.Typer()

# initialize database
services.database.session.migrate()


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
    with services.database.session.get() as db, services.graph.session.get() as neo:
        # db config
        struct_models = services.data_models.Slurp(db=db, toml_file=f"{config_path}/data_models.toml").call()
        struct_links = services.data_links.Slurp(db=db, toml_file=f"{config_path}/data_links.toml").call()
        struct_watches = services.entities.watches.Slurp(db=db, toml_file=f"{config_path}/entity_watches.toml").call()

        # db entities
        struct_entities = services.entities.Slurp(db=db, json_file=data_file).call()

        for entity_id in list(struct_entities.entity_ids):
            struct_watches_match = services.entities.watches.Match(
                db=db,
                neo=neo,
                entity_ids=[entity_id],
                topic="source",
            ).call()

            # publish entity messages
            services.entities.watches.Publish(
                watches=struct_watches_match.watches,
                entity_ids=[entity_id],
            ).call()

        logger.info(f"[db-cli] imported data models {struct_models.count}")
        logger.info(f"[db-cli] imported data links {struct_links.count}")
        logger.info(f"[db-cli] imported entity watches {struct_watches.count}")
        logger.info(f"[db-cli] imported entities {struct_entities.count}")


def _db_truncate():
    with services.database.session.get() as db, services.graph.session.get() as neo:
        services.graph.commands.truncate(neo)

        services.db.truncate_table(db=db, table_name="entities")
        services.db.truncate_table(db=db, table_name="entity_watches")
        services.db.truncate_table(db=db, table_name="data_links")
        services.db.truncate_table(db=db, table_name="data_models")

        logger.info("[db-cli] db and graph truncated")


if __name__ == "__main__":
    app()
