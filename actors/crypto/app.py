import logging
from dataclasses import dataclass

import toml  # type: ignore

import actors.crypto.workers.source
from models.actor import Actor


@dataclass
class Struct:
    code: int
    actors: dict
    errors: list[str]


class App:
    def __init__(self, toml_file: str) -> None:
        self._toml_file = toml_file

        self._toml_dict = toml.load(self._toml_file)
        self._app_name = self._toml_dict["name"]

        self._logger = logging.getLogger("actor")

    def call(self) -> Struct:
        struct = Struct(0, {}, [])

        # create actors with handlers

        toml_kafka = self._toml_dict["kafka"]

        actor_source = Actor(
            name=f"{self._app_name}-source",
            handler=actors.crypto.workers.source.WorkerSource(
                app_name=self._app_name,
            ),
            topic=toml_kafka["topic"],
            group=toml_kafka["group"],
        )

        struct.actors["source"] = actor_source

        # schedule actors

        for _, actor in struct.actors.items():
            actor.schedule()

        return struct
