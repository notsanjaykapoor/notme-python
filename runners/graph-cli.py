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
import services.graph

logger = logging_init("cli")

app = typer.Typer()


@app.command()
def graph_import(truncate: bool = typer.Option(...)):
    if truncate:
        services.graph.commands.truncate()
        logger.info(f"[graph-cli] truncated")

    with Session(engine) as db:
        struct = services.graph.Slurp(db=db).call()


@app.command()
def graph_nodes_count():
    query = "MATCH(n) return count(*) as count"
    records, summary = services.graph.query.execute_with_summary(query, {})

    for record in records:
        logger.info(f"[graph-cli] total nodes {record['count']}")

    query = "match(n)-[r]-(x) where (n:case or n:person or n:vehicle) return count(r) as count"
    records, summary = services.graph.query.execute_with_summary(query, {})

    records = services.graph.query.execute(query, {})

    for record in sorted(records, key=lambda record: -1 * record["count"]):
        logger.info(f"[graph-cli] total relationships {record['count']}")

    query = f"MATCH (n) RETURN distinct labels(n) as label, count(*) as count"
    records = services.graph.query.execute(query, {})

    for record in sorted(records, key=lambda record: -1 * record["count"]):
        logger.info(f"[graph-cli] node {record['label'][0]} {record['count']}")


@app.command()
def person_age_gt(min: int = typer.Option(...)):
    query = "MATCH (p:person)-[:has]->(n:age) WHERE n.value >= $min RETURN p as node,n.value as age"
    params = {"min": min}

    records = services.graph.query.execute(query, params)

    for record in sorted(records, key=lambda record: record["age"]):
        logger.info(f"[graph-cli] {record['node']['id']} age {record['age']}")


@app.command()
def person_age_lt(max: int = typer.Option(...)):
    query = "MATCH (p:person)-[:has]->(n:age) WHERE n.value <= $max RETURN p as node,n.value as age"
    params = {"max": max}

    records = services.graph.query.execute(query, params)

    for record in sorted(records, key=lambda record: record["age"]):
        logger.info(f"[graph-cli] {record['node']['id']} age {record['age']}")


@app.command()
def vehicle_make_eq(value: str = typer.Option(...)):
    query = "MATCH (v:vehicle)-[:has]->(n:make) WHERE n.value = $value RETURN v as node,n.value as value"
    params = {"value": value}

    records = services.graph.query.execute(query, params)

    for record in sorted(records, key=lambda record: record["value"]):
        logger.info(f"[graph-cli] {record['node']['id']} make {record['value']}")


@app.command()
def vehicle_makes():
    query = f"MATCH (s)-[:has]-(n:make) RETURN n.value as make, count(*) as count"

    records = services.graph.query.execute(query, {})

    for record in sorted(records, key=lambda record: -1 * record["count"]):
        logger.info(f"[graph-cli] {record['make']} {record['count']}")


@app.command()
def vehicle_stolen_eq(value: str = typer.Option(...)):
    query = "MATCH (v:vehicle)-[:has]->(n:stolen) WHERE n.value = $value RETURN v as node,n.value as value"
    params = {"value": value}

    records = services.graph.query.execute(query, params)

    for record in sorted(records, key=lambda record: record["value"]):
        logger.info(f"[graph-cli] {record['node']['id']} stolen {record['value']}")


if __name__ == "__main__":
    app()
