import logging
import os
import sys
import toml
import typing

from dataclasses import dataclass
from sqlmodel import select, Session

import models
import services.data_models
import services.graph


@dataclass
class Struct:
    code: int
    created: int
    exists: int
    errors: typing.List[str]


class Build:
    """create graph connections from data model connections"""

    def __init__(self, db: Session):
        self._db = db

    def call(self) -> Struct:
        struct = Struct(0, 0, 0, [])

        struct_list = services.data_models.List(
            db=self._db, query="", offset=0, limit=1000
        ).call()

        for data_model in struct_list.objects:
            connection_object = {
                "entity_name": data_model.object_name,
                "entity_slug": data_model.object_slug,
            }

            struct_create = services.graph.connections.Create(
                db=self._db,
                object=connection_object,
            ).call()

            if struct_create.code == 0:
                struct.created += 1
            elif struct_create.code == 409:
                struct.exists += 1

        return struct
