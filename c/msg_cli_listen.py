#!/usr/bin/env python
import asyncio
import os
import sys

import dotenv
import typer
import uvloop

sys.path.insert(1, os.path.join(sys.path[0], ".."))

dotenv.load_dotenv()

import database  # noqa: E402
import dog  # noqa: E402
import kafka  # noqa: E402
import log  # noqa: E402
import services.db  # noqa: E402
import services.entities  # noqa: E402
import services.entities.watches  # noqa: E402
import services.kafka.workers  # noqa: E402

logger = log.init("cli")

# initialize database
database.migrate()

# initialize datadog
dog.init()

# check kafka status
kafka.service_check()

app = typer.Typer()


@app.command()
def general():
    """listen on general topics for entity changes and graph sync"""
    uvloop.install()
    asyncio.run(general_async())


async def general_async():
    # schedule workers
    struct_worker_1 = kafka.Scheduler(
        topic=services.kafka.topics.TOPIC_ENTITY_CHANGES,
        group="group-1",
        handler=services.kafka.workers.EntityChanges(),
    ).call()

    struct_worker_2 = kafka.Scheduler(
        topic=services.kafka.topics.TOPIC_GRAPH_SYNC,
        group="group-1",
        handler=services.kafka.workers.GraphSync(),
    ).call()

    workers = [struct_worker_1, struct_worker_2]
    tasks = [s.task for s in workers]

    await asyncio.gather(*tasks)
