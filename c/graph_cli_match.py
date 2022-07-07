#!/usr/bin/env python

from dotenv import load_dotenv

load_dotenv()

import os  # noqa: E402
import sys  # noqa: E402

import datadog  # noqa: E402
import typer  # noqa: E402

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import log  # noqa: E402
import services.database.session  # noqa: E402
import services.entities  # noqa: E402
import services.graph.distance  # noqa: E402
import services.graph.query  # noqa: E402
import services.graph.session  # noqa: E402
import services.graph.tx  # noqa: E402

logger = log.init("cli")

app = typer.Typer()


@app.command()
def edges(
    node: str = typer.Option(...),
):
    """find all node edges"""

    node_name, node_id = node.split(":", 1)

    struct_graph = services.graph.query.match_edges(
        src_label=node_name,
        src_id=node_id,
    )

    logger.info(f"[graph-cli] query '{struct_graph.query}' params {struct_graph.params}")

    with datadog.statsd.timed(f"{__name__}.timer", tags=["env:dev", "neo:read"]):
        with services.graph.session.get() as neo:
            records = neo.read_transaction(services.graph.tx.read, struct_graph.query, struct_graph.params)

    if not records:
        logger.info("[graph-cli] no records found")

    for i, record in enumerate(records):
        logger.info("")

        logger.info(f"[graph-cli] record {i+1} {record}")


@app.command()
def geo(
    node: str = typer.Option(...),
    radius: str = typer.Option(None, "--radius", "-r"),
):
    """find node neighbors within specified distance"""

    name, id = node.split(":", 1)

    meters = services.graph.distance.meters(radius)

    struct_graph = services.graph.query.match_geo_distance_from_node(
        src_label=name,
        src_id=id,
        meters=meters,
    )

    # struct_graph = services.graph.query.match_geo_distance_from_point(
    #     lat=41.8911752,
    #     lon=-87.6321491,
    #     dst_label="place",
    #     dst_id="01G5YPTKXDWA1DC19W2963SJZW",
    #     meters=meters,
    # )

    logger.info(f"[graph-cli] query '{struct_graph.query}' params {struct_graph.params}")

    with datadog.statsd.timed(f"{__name__}.timer", tags=["env:dev", "neo:read"]):
        with services.graph.session.get() as neo:
            records = neo.read_transaction(services.graph.tx.read, struct_graph.query, struct_graph.params)

    if not records:
        logger.info("[graph-cli] no records found")

    for i, record in enumerate(records):
        logger.info("")

        logger.info(f"[graph-cli] record {i+1} {record}")


@app.command()
def neighbors(
    node: str = typer.Option(...),
    dst_label: str = typer.Option(None),
    max_hops: int = typer.Option(1),
):
    """find all node neighbors filtered by label and constrained by hops"""

    node_name, node_id = node.split(":", 1)

    # with services.database.session.get() as db:
    #     struct_list = services.entities.ListEntityNames(db).call()
    #     # map to list of list values, e.g. [['case'], ['person']]
    #     dst_labels = [[s] for s in struct_list.values]

    struct_graph = services.graph.query.match_neighbors(
        src_label=f"{node_name}:entity",
        src_id=node_id,
        max_hops=max_hops,
        dst_label=dst_label,
    )

    logger.info(f"[graph-cli] query '{struct_graph.query}' params {struct_graph.params}")

    with services.graph.session.get() as neo:
        records = neo.read_transaction(services.graph.tx.read, struct_graph.query, struct_graph.params)

    if not records:
        logger.info("[graph-cli] no records found")

    for i, record in enumerate(records):
        logger.info("")

        path = record["path"]
        nodes = path.nodes
        edges = path.relationships

        logger.info(f"[graph-cli] record {i+1}")
        logger.info(f"[graph-cli] path {path}")
        logger.info(f"[graph-cli] nodes {nodes}")
        logger.info(f"[graph-cli] edges {edges}")

        # node_start = record["s"]
        # node_end = record["e"]
        # relationships = record["r"]

        # logger.info(f"[graph-cli] start {node_start}")
        # logger.info(f"[graph-cli] end {node_end}")
        # logger.info(f"[graph-cli] rels {relationships}")


@app.command()
def shortest_path(
    node_1: str = typer.Option(...),
    node_2: str = typer.Option(...),
):
    """find all shortest paths between nodes"""

    src_label, src_id = node_1.split(":", 1)
    dst_label, dst_id = node_2.split(":", 1)

    # struct_graph = services.graph.query.match_shortest_path(
    #     src_label=src_label,
    #     src_id=src_id,
    #     dst_label=dst_label,
    #     dst_id=dst_id,
    # )

    query = f"""
    match (p1:{src_label} {{id: $src_id}}), (p2:{dst_label} {{id: $dst_id}}), p = allShortestPaths((p1)-[r*]-(p2)) return p
    """

    params = {
        "src_id": src_id,
        "dst_id": dst_id,
    }

    logger.info(f"[graph-cli] query '{query}' params {params}")

    with services.graph.session.get() as neo:
        records = neo.read_transaction(services.graph.tx.read, query, params)

    if not records:
        logger.info("[graph-cli] no path found")

    for i, record in enumerate(records):
        logger.info("")

        path = record["p"]

        logger.info(f"[graph-cli] path {i+1}")

        for node in path.nodes:
            logger.info(f"[graph-cli] node {node.labels} {node.items()}")


if __name__ == "__main__":
    app()
