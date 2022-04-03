import asyncio
import logging

from dataclasses import dataclass

import actors.example.workers.echo as echo
import actors.example.workers.source as wsource
import actors.factory as factory
import actors.source as source

@dataclass
class Struct:
  code: int
  actors: {}
  errors: list[str]

class App:
  def __init__(self, name: str = "example"):
    self._name = name

    self._actors = {}
    self._source = { # kafka topic and group
      "topic": "example",
      "group": "group",
    }
    self._stages = {
      "source": ["echo"],
    }
    self._logger = logging.getLogger("actor")

  def call(self):
    struct = Struct(0, {}, [])

    self._logger.info(f"{__name__} '{self._name}' starting")

    # create actors

    struct_source = source.ActorSource(
      name=f"{self._name}-source",
      topic=self._source["topic"],
      group=self._source["group"],
      handler=wsource.WorkerSource(
        actor_name=f"{self._name}-source"
      ),
    ).call()

    self._actors["source"] = struct_source.actor

    struct_factory = factory.ActorFactory(
      name=f"{self._name}-echo",
      handler=echo.WorkerEcho(
        actor_name=f"{self._name}-echo"
      ),
    ).call()

    self._actors["echo"] = struct_factory.actor

    # stitch pipepline together by setting output queues for each stage

    for key, actor_names in self._stages.items():
      actor_from = self._actors[key]
      for actor_name in actor_names:
        actor_to = self._actors[actor_name]
        actor_from.output = actor_to.queue

    struct.actors = self._actors

    self._logger.info(f"{__name__} '{self._name}' completed")

    return struct
