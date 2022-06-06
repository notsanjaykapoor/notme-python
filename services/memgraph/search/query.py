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


def query(query: str, params: dict, connection: models.MemgraphConnection) -> Struct:
    struct = Struct(0, 0, [], [])

    cursor = connection.cursor()
    cursor.execute(query, params)

    struct.count = cursor.rowcount
    struct.objects = cursor.fetchall()

    return struct
