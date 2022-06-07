import logging
import os
import sys
import toml
import typing

from dataclasses import dataclass
from sqlmodel import select, Session

import models
import services.graph


@dataclass
class Struct:
    code: int
    created: int
    exists: int
    errors: typing.List[str]


class Factory:
    def __init__(self, db: Session, toml_file: str):
        self._db = db
        self._toml_file = toml_file

        self._toml_dict = toml.load(self._toml_file)

    def call(self) -> Struct:
        struct = Struct(0, 0, 0, [])

        connections = self._toml_dict["connections"]

        for object in connections:
            struct_create = services.graph.connections.Create(
                db=self._db,
                object=object,
            ).call()

            if struct_create.code == 0:
                struct.created += 1
            elif struct_create.code == 409:
                struct.exists += 1

        return struct
