from dataclasses import dataclass

import logging
import sys
import typing

import models


@dataclass
class Struct:
    code: int
    count: int
    objects: list[typing.Any]
    errors: list[str]


class Query:
    def __init__(
        self,
        query: str,
        params: dict,
        connection: models.MemgraphConnection,
    ):
        self._query = query
        self._params = params
        self._connection = connection

        self._cursor = self._connection.cursor()
        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [], [])

        self._cursor.execute(self._query, self._params)

        struct.count = self._cursor.rowcount
        struct.objects = self._cursor.fetchall()

        return struct
