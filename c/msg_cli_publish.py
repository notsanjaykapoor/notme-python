#!/usr/bin/env python
import os
import sys

import typer

import stats_init  # noqa: F401
import dot_init  # noqa: F401

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import kafka  # noqa: E402
import log  # noqa: E402
import models  # noqa: E402
import services.database.session  # noqa: E402
import services.db  # noqa: E402
import services.entities  # noqa: E402
import services.entities.watches  # noqa: E402

logger = log.init("cli")

# initialize database
services.database.session.migrate()

# check kafka status
kafka.service_check()

app = typer.Typer()


@app.command()
def change(
    topic_name: str = typer.Option(services.kafka.topics.TOPIC_ENTITY_CHANGES, "--topic", help="kafka topic"),
):
    """publish random entity change message"""
    logger.info("[db-cli] publish try")

    with services.database.session.get() as db:
        entity = services.entities.get_random(db)

    if not entity:
        logger.info("[db-cli] publish error")
        return

    assert entity.id

    message = models.Entity.message_changed_cls(entity.id)

    services.entities.Publish(message=message, topic=topic_name).call()

    logger.info("[db-cli] publish completed")


@app.command()
def error(
    topic_name: str = typer.Option(services.kafka.topics.TOPIC_ENTITY_CHANGES, "--topic", help="kafka topic"),
):
    """publish random entity 422 message"""

    logger.info("[db-cli] publish try")

    with services.database.session.get() as db:
        entity = services.entities.get_random(db)

    if not entity:
        logger.info("[db-cli] publish error")
        return

    assert entity.id

    message = models.Entity.message_changed_cls(entity.id)
    message["name"] = "entity.422"

    services.entities.Publish(message=message, topic=topic_name).call()

    logger.info("[db-cli] publish completed")
