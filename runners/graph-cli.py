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
def graph_import(truncate: bool = typer.Option(...)):
    if truncate:
        services.neo.commands.truncate()
        logger.info(f"[graph-cli] truncated")

    with Session(engine) as db:
        struct = services.neo.Slurp(db=db).call()


@app.command()
def graph_node_count():
    query = "MATCH(n) return count(*) as count"
    records, summary = services.neo.query.execute_with_summary(query, {})

    for record in records:
        logger.info(f"[graph-cli] total {record['count']}")

    query = f"MATCH (n) RETURN distinct labels(n) as label, count(*) as count"

    records = services.neo.query.execute(query, {})

    for record in sorted(records, key=lambda record: -1 * record["count"]):
        logger.info(f"[graph-cli] {record['label'][0]} {record['count']}")


@app.command()
def person_age_gt(min: int = typer.Option(...)):
    query = "MATCH (p:person)-[:HAS]->(n:age) WHERE n.value >= $min RETURN p as node,n.value as age"
    params = {"min": min}

    records = services.neo.query.execute(query, params)

    for record in sorted(records, key=lambda record: record["age"]):
        logger.info(f"[graph-cli] {record['node']['id']} age {record['age']}")


@app.command()
def person_age_lt(max: int = typer.Option(...)):
    query = "MATCH (p:person)-[:HAS]->(n:age) WHERE n.value <= $max RETURN p as node,n.value as age"
    params = {"max": max}

    records = services.neo.query.execute(query, params)

    for record in sorted(records, key=lambda record: record["age"]):
        logger.info(f"[graph-cli] {record['node']['id']} age {record['age']}")


@app.command()
def vehicle_make_eq(value: str = typer.Option(...)):
    query = "MATCH (v:vehicle)-[:HAS]->(n:make) WHERE n.value = $value RETURN v as node,n.value as value"
    params = {"value": value}

    records = services.neo.query.execute(query, params)

    for record in sorted(records, key=lambda record: record["value"]):
        logger.info(f"[graph-cli] {record['node']['id']} make {record['value']}")


@app.command()
def vehicle_makes():
    query = f"MATCH (s)-[:HAS]-(n:make) RETURN n.value as make, count(*) as count"

    records = services.neo.query.execute(query, {})

    for record in sorted(records, key=lambda record: -1 * record["count"]):
        logger.info(f"[graph-cli] {record['make']} {record['count']}")


@app.command()
def vehicle_stolen_eq(value: str = typer.Option(...)):
    query = "MATCH (v:vehicle)-[:HAS]->(n:stolen) WHERE n.value = $value RETURN v as node,n.value as value"
    params = {"value": value}

    records = services.neo.query.execute(query, params)

    for record in sorted(records, key=lambda record: record["value"]):
        logger.info(f"[graph-cli] {record['node']['id']} stolen {record['value']}")


if __name__ == "__main__":
    app()
