import logging
from dataclasses import dataclass

import sqlmodel
import toml

import services.data_links


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

        for object in self._toml_dict["links"]:
            struct_create = services.data_links.Create(
                db=self._db,
                objects=[object],
            ).call()

            struct.count += struct_create.count

        return struct
