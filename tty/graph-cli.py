from dotenv import load_dotenv

load_dotenv()

import json
import os
import sys
import typer

from sqlmodel import Session, SQLModel

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from log import logging_init

import database
import models
import services.db
import services.entities
import services.graph
import services.graph.build
import services.graph.commands
import services.graph.driver
import services.graph.stream

logger = logging_init("cli")

app = typer.Typer()


# initialize database
database.migrate(database.engine)


@app.command()
def graph_build(truncate: bool = typer.Option(...)):
    if truncate:
        services.graph.commands.truncate()
        logger.info(f"[graph-cli] truncated")

    with Session(database.engine) as db:
        with services.graph.driver.get() as driver:
            offset = 0
            limit = 1000

            while True:
                struct_list = services.entities.List(
                    db=db, query="", offset=offset, limit=limit
                ).call()

                if not struct_list.objects:
                    break

                for entity in struct_list.objects:
                    services.graph.stream.Process(
                        db=db, driver=driver, entity=entity
                    ).call()

                offset += limit

    graph_count()


@app.command()
def graph_count():
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
def match_neighbors(
    node: str = typer.Option(...),
    max_hops: int = typer.Option(...),
):
    name, id = node.split(":", 1)

    query = (
        f"match p = (s:{name} {{id: $id_1}})-[r*1.."
        + str(max_hops)
        + f"]-(e) return s,e,relationships(p) as r"
    )

    params = {
        "id_1": id,
    }

    logger.info(f"[graph-cli] {query} {params}")

    records = services.graph.query.execute(query, params)

    if not records:
        logger.info(f"[graph-cli] no records found")

    for i, record in enumerate(records):
        logger.info("")
        node_start = record["s"]
        node_end = record["e"]
        relationships = record["r"]

        import ipdb

        # ipdb.set_trace()

        logger.info(f"[graph-cli] record {i+1}")
        logger.info(f"[graph-cli] start {node_start}")
        logger.info(f"[graph-cli] end {node_end}")
        logger.info(f"[graph-cli] rels {relationships}")


@app.command()
def match_shortest_path(
    node_1: str = typer.Option(...),
    node_2: str = typer.Option(...),
):
    name_1, id_1 = node_1.split(":", 1)
    name_2, id_2 = node_2.split(":", 1)

    query = f"match (p1:{name_1} {{id: $id_1}}), (p2:{name_2} {{id: $id_2}}), p = allShortestPaths((p1)-[r*]-(p2)) return p"

    params = {
        "id_1": id_1,
        "id_2": id_2,
    }

    logger.info(f"[graph-cli] {query} {params}")

    records = services.graph.query.execute(query, params)

    if not records:
        logger.info(f"[graph-cli] no path found")

    for i, record in enumerate(records):
        logger.info("")

        path = record["p"]

        logger.info(f"[graph-cli] path {i+1}")

        for node in path.nodes:
            logger.info(f"[graph-cli] node {node.labels} {node.values()}")


@app.command()
def person_age_gt(min: int = typer.Option(...)):
    query = "MATCH (p:person)-[:has]-(n:age) WHERE n.value >= $min RETURN p as node,n.value as age"
    params = {"min": min}

    records = services.graph.query.execute(query, params)

    for record in sorted(records, key=lambda record: record["age"]):
        logger.info(f"[graph-cli] {record['node']['id']} age {record['age']}")


@app.command()
def person_age_lt(max: int = typer.Option(...)):
    query = "MATCH (p:person)-[:has]-(n:age) WHERE n.value <= $max RETURN p as node,n.value as age"
    params = {"max": max}

    records = services.graph.query.execute(query, params)

    for record in sorted(records, key=lambda record: record["age"]):
        logger.info(f"[graph-cli] {record['node']['id']} age {record['age']}")


@app.command()
def vehicle_make_eq(value: str = typer.Option(...)):
    query = "MATCH (v:vehicle)-[:has]-(n:make) WHERE n.value = $value RETURN v as node,n.value as value"
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
