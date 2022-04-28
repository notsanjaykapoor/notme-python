from dataclasses import dataclass

import logging
import sys
import typing

from models.memgraph_connection import MemgraphConnection

@dataclass
class Struct:
  code: int
  count: int
  objects: list[typing.Any]
  errors: list[str]

class MemgraphQuery:
  def __init__(self, query: str, connection: MemgraphConnection = MemgraphConnection()):
    self._query = query
    self._connection = connection

    self._cursor = self._connection.cursor()
    self._logger = logging.getLogger("service")

  def call(self):
    struct = Struct(0, 0, [], [])

    self._cursor.execute(self._query)

    struct.count = self._cursor.rowcount
    struct.objects = self._cursor.fetchall()

    return struct
