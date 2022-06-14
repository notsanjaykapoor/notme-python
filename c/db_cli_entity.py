#!/usr/bin/env python

import asyncio
import os
import sys

import dotenv
import uvloop

sys.path.insert(1, os.path.join(sys.path[0], ".."))

dotenv.load_dotenv()

import sqlalchemy  # noqa: E402
import sqlmodel  # noqa: E402
import typer  # noqa: E402

import database  # noqa: E402
import kafka  # noqa: E402
import log  # noqa: E402
import models  # noqa: E402
import services.entities  # noqa: E402
import services.entities.messages  # noqa: E402
import services.kafka.workers  # noqa: E402

logger = log.init("cli")

app = typer.Typer()

# initialize database
database.migrate()


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


@app.command()
def publish_change(
    entity_id: int = typer.Option(..., "--id", help="entity id"),
    kafka_topic: str = typer.Option("entity-changes", "--topic", help="kafka topic"),
):
    message = services.entities.messages.create(entity_id)

    logger.info("[db-cli] publish try")

    services.entities.messages.Publish(message=message, topic=kafka_topic).call()

    logger.info("[db-cli] publish completed")


@app.command()
def publish_delete(
    entity_id: int = typer.Option(..., "--id", help="entity id"),
    kafka_topic: str = typer.Option("entity-changes", "--topic", help="kafka topic"),
):
    pass


@app.command()
def read_wait():
    uvloop.install()
    asyncio.run(read_wait_async())


async def read_wait_async():
    # schedule tasks
    struct_scheduler = kafka.Scheduler(
        topic="entity-changes",
        group="group-1",
        handler=services.kafka.workers.EntityChanges(),
    ).call()

    tasks = []

    # get tasks
    tasks.append(struct_scheduler.task)

    await asyncio.gather(*tasks)
