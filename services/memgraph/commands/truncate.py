import logging
import sys
import typing
from dataclasses import dataclass

import models


@dataclass
class Struct:
    code: int
    errors: list[str]


def truncate(connection: models.MemgraphConnection) -> int:
    cursor = connection.cursor()
    cursor.execute(connection.query_delete_all())
    return 0
