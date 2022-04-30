from dotenv import load_dotenv

load_dotenv()

import json
import os
import sys
import typer

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from log import logging_init

from models.memgraph_connection import MemgraphConnection
from services.memgraph.parse.record import MemgraphParseRecord
from services.memgraph.query import MemgraphQuery

logger = logging_init("cli")

app = typer.Typer()

@app.command()
def graph_create(max: int = typer.Option(...)):
  connection = MemgraphConnection()

  cursor = connection.cursor()

  # delete all nodes
  cursor.execute(connection.query_delete_all())

  # Create a node with the label FirstNode and message property with the value "Hello, World!"
  # query = """
  #   CREATE (n:FirstNode)
  #   SET n.message = '{message}'
  #   RETURN 'Node '  + id(n) + ': ' + n.message""".format(message="Hello, World!")

  print("json import starting")

  file = "./data/example/graph.json"
  data = json.load(open(file))
  count = 0

  for record in data:
    struct_parse = MemgraphParseRecord(connection, record).call()

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
def query_person_age(min: int = typer.Option(...)):
  query = f"MATCH (p:person)-[:HAS]->(n:age) WHERE n.value >= {min} RETURN p,n.value"
  struct_query = MemgraphQuery(query).call()

  print(f"query 'age gte {min}' count {struct_query.count}")

  for object in struct_query.objects:
    print(object)

@app.command()
def query_vehicle_make(name: str = typer.Option(...)):
  query = f"MATCH (v:vehicle)-[:HAS]->(n:make) WHERE n.value = '{name}' RETURN v,n.value"
  struct_query = MemgraphQuery(query).call()

  print(f"query 'vehicle make eq {name}' count {struct_query.count}")

  for object in struct_query.objects:
    print(object)

if __name__ == "__main__":
  app()
