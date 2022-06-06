from dataclasses import dataclass

import logging
import mgclient
import sys
import typing

import models


@dataclass
class QueryResult:
    node: "mgclient.Node"
    age: int


@dataclass
class Struct:
    code: int
    count: int
    objects: list[QueryResult]
    errors: list[str]


class PersonAgeGt:
    def __init__(
        self,
        min: int,
        connection: models.MemgraphConnection,
    ):
        self._min = min
        self._connection = connection

        self._query = (
            "MATCH (p:person)-[:HAS]->(n:age) WHERE n.value >= $min RETURN p,n.value"
        )
        self._params = {"min": self._min}

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
