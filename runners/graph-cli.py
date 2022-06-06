from dotenv import load_dotenv

load_dotenv()

import json
import os
import sys
import typer

from sqlmodel import Session, SQLModel

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from database import engine
from log import logging_init

import models
import services.db
import services.entities
import services.neo

logger = logging_init("cli")

app = typer.Typer()


@app.command()
def entity_count():
    count = services.neo.query.get_entity_count()

    logger.info(f"[graph-cli] entity count {count}")


@app.command()
def entity_import(truncate: bool = typer.Option(...)):
    if truncate:
        services.neo.truncate()
        logger.info(f"[graph-cli] truncated")

    with Session(engine) as db:
        struct = services.neo.Slurp(db=db).call()


@app.command()
def person_age_gt(min: int = typer.Option(...)):
    query = "MATCH (p:person)-[:HAS]->(n:age) WHERE n.value >= $min RETURN p as node,n.value as age"
    params = {"min": min}

    records = services.neo.query.get(query, params)

    for record in sorted(records, key=lambda record: record["age"]):
        logger.info(f"[graph-cli] {record['node']['id']} age {record['age']}")


@app.command()
def person_age_lt(max: int = typer.Option(...)):
    query = "MATCH (p:person)-[:HAS]->(n:age) WHERE n.value <= $max RETURN p as node,n.value as age"
    params = {"max": max}

    records = services.neo.query.get(query, params)

    for record in sorted(records, key=lambda record: record["age"]):
        logger.info(f"[graph-cli] {record['node']['id']} age {record['age']}")


@app.command()
def vehicle_make_eq(name: str = typer.Option(...)):
    query = "MATCH (v:vehicle)-[:HAS]->(n:make) WHERE n.value = $name RETURN v as node,n.value as make"
    params = {"name": name}

    records = services.neo.query.get(query, params)

    for record in sorted(records, key=lambda record: record["make"]):
        logger.info(f"[graph-cli] {record['node']['id']} make {record['make']}")


@app.command()
def vehicle_makes():
    query = f"MATCH (s)-[:HAS]-(n:make) RETURN n.value as make, count(*) as count"

    records = services.neo.query.get(query, {})

    for record in sorted(records, key=lambda record: -1 * record["count"]):
        logger.info(f"[graph-cli] {record['make']} {record['count']}")


if __name__ == "__main__":
    app()
