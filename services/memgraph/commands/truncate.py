from dataclasses import dataclass

import logging
import sys
import typing

import models


@dataclass
class Struct:
    code: int
    errors: list[str]


def truncate(connection: models.MemgraphConnection) -> int:
    cursor = connection.cursor()
    cursor.execute(connection.query_delete_all())
    return 0
