import asyncio
import logging
import toml

from dataclasses import dataclass

import actors.example.workers.echo
import actors.example.workers.source

from models.actor import Actor


@dataclass
class Struct:
    code: int
    actors: {}
    errors: list[str]


class App:
    def __init__(self, toml_file: str):
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
            topic=toml_kafka["topic"],
            group=toml_kafka["group"],
        )

        actor_source.handler = actors.example.workers.source.WorkerSource(
            actor=actor_source,
            app_name=self._app_name,
        )

        struct.actors["source"] = actor_source

        actor_echo = Actor(
            name=f"{self._app_name}-echo",
        )

        actor_echo.handler = actors.example.workers.echo.WorkerEcho(
            actor=actor_echo,
            app_name=self._app_name,
        )

        struct.actors["echo"] = actor_echo

        # stitch pipepline together by setting output queues for each stage

        toml_stages = self._toml_dict["stages"]

        for actor_src_name, actor_dst_names in toml_stages.items():
            actor_src = struct.actors[actor_src_name]

            for actor_dst_name in actor_dst_names:
                # set actor src output queue == actor dst input queue
                actor_dst = struct.actors[actor_dst_name]
                actor_src.output = actor_dst.queue

        # schedule actors

        for _, actor in struct.actors.items():
            actor.schedule()

        return struct
