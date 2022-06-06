from dataclasses import dataclass

import logging
import mgclient
import sys
import typing

import models


@dataclass
class QueryResult:
    node: "mgclient.Node"
    make: str


@dataclass
class Struct:
    code: int
    count: int
    objects: list[QueryResult]
    errors: list[str]


class VehicleMakeEq:
    def __init__(
        self,
        name: str,
        connection: models.MemgraphConnection,
    ):
        self._name = name
        self._connection = connection

        self._query = (
            f"MATCH (v:vehicle)-[:HAS]->(n:make) WHERE n.value = $name RETURN v,n.value"
        )
        self._params = {"name": self._name}

        self._cursor = self._connection.cursor()
        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [], [])

        self._cursor.execute(self._query, self._params)

        struct.count = self._cursor.rowcount
        struct.objects = [
            QueryResult(record[0], record[1]) for record in self._cursor.fetchall()
        ]

        return struct
