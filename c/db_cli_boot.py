#!/usr/bin/env python
import os
import sys

import typer

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import dot_init  # noqa: E402, F401
import log  # noqa: E402
import services.boot  # noqa: E402
import services.cities  # noqa: E402
import services.data_links  # noqa: E402
import services.data_models  # noqa: E402
import services.database  # noqa: E402
import services.entities  # noqa: E402
import services.entity_watches  # noqa: E402
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
    services.boot.reset()

    os.system("./c/graph-cli sync geo")


def _db_publish(entity_ids: set[str]):
    logger.info(f"[db-cli] publish entities {len(entity_ids)}")

    with services.database.session.get() as db, services.graph.session.get() as neo:
        for entity_id in entity_ids:
            struct_watches_match = services.entity_watches.Match(
                db=db,
                neo=neo,
                entity_ids=[entity_id],
                topic="source",
            ).call()

            # publish entity messages
            services.entity_watches.Publish(
                watches=struct_watches_match.watches,
                entity_ids=[entity_id],
            ).call()

    logger.info("[db-cli] publish completed")


if __name__ == "__main__":
    app()
