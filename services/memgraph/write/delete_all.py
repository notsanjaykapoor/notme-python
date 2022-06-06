from dataclasses import dataclass

import logging
import sys
import typing

import models


@dataclass
class Struct:
    code: int
    errors: list[str]


class DeleteAll:
    def __init__(
        self,
        connection: models.MemgraphConnection,
    ):
        self._connection = connection

        self._cursor = self._connection.cursor()
        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, [])

        # delete all nodes
        self._cursor.execute(self._connection.query_delete_all())

        return struct
