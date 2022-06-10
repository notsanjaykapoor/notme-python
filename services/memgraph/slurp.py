from dataclasses import dataclass

import logging
import sys

from dataclasses import dataclass
from sqlmodel import select, Session
from typing import List

import models
import services.entities


@dataclass
class Struct:
    code: int
    count: int
    errors: List[str]


class Slurp:
    def __init__(self, db: Session, offset: int = 0, limit: int = 1000):
        self._db = db
        self._logger = logging.getLogger("service")

        self._offset = offset
        self._limit = limit

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        # find entities
        while True:
            struct_list = services.entities.List(
                db=self._db,
                query="",
                offset=self._offset,
                limit=self._limit,
            ).call()

            self._logger.info(f"{__name__} {struct_list.count}")

            if not struct_list.objects:
                break

            self._offset += self._limit

        return struct
