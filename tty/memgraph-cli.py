#!/usr/bin/env python

from dotenv import load_dotenv

load_dotenv()

import json
import os
import sys
import typer

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from log import logging_init

import models
import services.memgraph

logger = logging_init("cli")

app = typer.Typer()


@app.command()
def graph_create(file: str = typer.Option(...), max: int = typer.Option(...)):
    connection = models.MemgraphConnection()

    struct_delete = services.memgraph.commands.truncate(connection)

    cursor = connection.cursor()

    # delete all nodes
    cursor.execute(connection.query_delete_all())

    # Create a node with the label FirstNode and message property with the value "Hello, World!"
    # query = """
    #   CREATE (n:FirstNode)
    #   SET n.message = '{message}'
    #   RETURN 'Node '  + id(n) + ': ' + n.message""".format(message="Hello, World!")

    print("json import starting")

    objects = json.load(open(file))
    count = 0

    for record in objects:
        struct_parse = services.memgraph.Load(connection, record).call()

        if struct_parse.code == 0:
            count += 1
        else:
            print(f"skipping ... {record}")

        if count >= max:
            break

    connection.commit()

    print("json import completed")

    cursor.execute(connection.query_match_all())
    print(f"query nodes count {cursor.rowcount}")


@app.command()
def vehicle_makes_group():
    """Group vehicle makes by make and count"""

    query = "match (n)-[r]-(m:make) return m.value, count(*)"

    struct_result = services.memgraph.search.query(query, {}).call()

    for object in sorted(struct_result.objects, key=lambda object: object[0]):
        print(object)


@app.command()
def vehicle_makes_list():
    """Find all distinct vehicle makes"""

    query = "match (m:make) return m.value"

    struct_result = services.memgraph.search.query(query, {}).call()

    for object in sorted(struct_result.objects, key=lambda object: object[0]):
        print(object)


if __name__ == "__main__":
    app()
