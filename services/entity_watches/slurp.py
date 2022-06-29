from dataclasses import dataclass

import sqlmodel
import toml

import services.entities
import services.entity_watches
import services.kafka.topics


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

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        for object in self._toml_dict["watches"]:
            # persist to database
            struct_create = services.entity_watches.Create(
                self._db,
                objects=[object],
            ).call()

            if struct_create.code == 0:
                struct.count += struct_create.count

        return struct
