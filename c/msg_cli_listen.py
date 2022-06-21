#!/usr/bin/env python
import asyncio
import os
import sys

import typer
import uvloop

import dot_init  # noqa: F401
import stats_init  # noqa: F401

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import kafka  # noqa: E402
import log  # noqa: E402
import services.database.session  # noqa: E402
import services.db  # noqa: E402
import services.entities  # noqa: E402
import services.entities.watches  # noqa: E402
import services.kafka.topics  # noqa: E402
import services.kafka.workers  # noqa: E402

logger = log.init("cli")

# initialize database
services.database.session.migrate()

# check kafka status
kafka.service_check()

app = typer.Typer()


@app.command()
def graph():
    """listen on graph sync topics"""
    uvloop.install()
    asyncio.run(graph_async())


async def graph_async():
    workers = []

    workers.append(
        kafka.Scheduler(
            topic=services.kafka.topics.TOPIC_GRAPH_SYNC,
            group="group-1",
            handler=services.kafka.workers.GraphHandler(),
        ).call()
    )

    workers.append(
        kafka.Scheduler(
            topic=services.kafka.topics.TOPIC_GEOFENCE_ALERTS,
            group="group-1",
            handler=services.kafka.workers.GeofenceHandler(),
        ).call()
    )

    tasks = [s.task for s in workers]

    await asyncio.gather(*tasks)
