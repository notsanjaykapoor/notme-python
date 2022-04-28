from dataclasses import dataclass

import logging
import sys
import typing

from models.memgraph_connection import MemgraphConnection

@dataclass
class Struct:
  code: int
  errors: list[str]

class MemgraphParseRecord:
  def __init__(self, connection: MemgraphConnection, record: dict):
    self._connection = connection
    self._record = record
    self._logger = logging.getLogger("service")

    self._model = self._record["model"]
    self._id = self._record["id"]
    self._model = self._record["model"]
    self._record_props = self._record["properties"]

    if self._model == "person":
      self._props_list = ["first_name", "last_name"]
    else: # case, vehicle
      self._props_list = []

  def call(self):
    struct = Struct(0, [])

    self._create_node_model()
    self._create_node_others()
    self._create_relationships()

    return struct

  def _create_node_model(self):
    props_list = list(filter(lambda o : o["slug"] in self._props_list, self._record_props))

    props_dict = {
      "id": self._id
    }

    for dict_ in props_list:
      props_dict[dict_["slug"]] = dict_["value"]

    # create person node

    query = f"CREATE (p:{self._model} $params) RETURN p"

    params = {
      "params": props_dict
    }

    self._logger.info(f"{__name__} create {query} {params}")

    self._connection.cursor().execute(query, params)

  def _create_node_others(self):
    relationships_list = list(filter(lambda o : o["slug"] not in self._props_list, self._record_props))

    for dict_ in relationships_list:
      node_name = dict_["slug"]
      node_value = dict_["value"]
      node_type = dict_["type"]

      if node_value is None:
        continue

      node_dict = {
        'value': node_value
      }

      if node_type == "integer":
        # no quote
        query = f"MERGE (n:{node_name} " + "{value: " + f"{node_value}" + "}) RETURN n"
      else:
        query = f"MERGE (n:{node_name} " + "{value: " + f"'{node_value}'" + "}) RETURN n"

      self._logger.info(f"{__name__} create {query}")

      self._connection.cursor().execute(query)

  def _create_relationships(self):
    relationships_list = list(filter(lambda o : o["slug"] not in self._props_list, self._record_props))

    for dict_ in relationships_list:
      rel_name = dict_["slug"]
      rel_value = dict_["value"]

      query = f"""
        MATCH (n1:{self._model}), (n2:{rel_name})
        WHERE n1.id = '{self._id}' and n2.value = $rel_value
        CREATE (n1)-[r:HAS]->(n2)
      """

      params = {
        "rel_value": rel_value,
      }

      # self._logger.info(f"{__name__} create {query} {params}")

      self._connection.cursor().execute(query, params)
