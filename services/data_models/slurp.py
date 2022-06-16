import logging
from dataclasses import dataclass

import sqlmodel
import toml

import services.data_models


@dataclass
class Struct:
    code: int
    count: int
    errors: list[str]


class Slurp:
    def __init__(self, db: sqlmodel.Session, toml_file: str):
        self._db = db
        self._toml_file = toml_file

        self._toml_dict = toml.load(self._toml_file)

        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        data_model_names = self._toml_dict.keys()

        for name in data_model_names:
            objects = []

            for dict in self._toml_dict[name].values():
                object = {
                    "object_name": name,
                    "object_node": dict["node"],
                    "object_slug": dict["slug"],
                    "object_type": dict["type"],
                }

                objects.append(object)

            struct_create = services.data_models.Create(
                db=self._db,
                objects=objects,
            ).call()

            if struct_create.code == 0:
                struct.count += struct_create.object_count

        return struct
