import logging
import toml

from dataclasses import dataclass
from sqlmodel import select, Session

import services.data_models


@dataclass
class Struct:
    code: int
    created: int
    errors: list[str]


class Slurp:
    def __init__(self, db: Session, toml_file: str):
        self._db = db
        self._toml_file = toml_file

        self._toml_dict = toml.load(self._toml_file)

        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        data_model_names = self._toml_dict.keys()

        for name in data_model_names:
            objects: list[dict] = []

            for dict in self._toml_dict[name].values():
                object = {
                    "object_name": name,
                    "object_slug": dict["slug"],
                    "object_type": dict["type"],
                }

                objects.append(object)

            struct_create = services.data_models.Create(
                db=self._db,
                objects=objects,
            ).call()

            if struct_create.code == 0:
                struct.created += struct_create.object_count

        return struct
