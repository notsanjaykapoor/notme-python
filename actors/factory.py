import asyncio
import logging
import typing

from dataclasses import dataclass

from models.actor import Actor

@dataclass
class Struct:
  code: int
  actor: Actor
  errors: list[str]

class ActorFactory:
  def __init__(self, name: str, handler: typing.Any, queue: asyncio.Queue = None):
    self._name = name
    self._handler = handler
    self._queue = queue

    if self._queue is None:
      self._queue = asyncio.Queue(maxsize=0)

    self._logger = logging.getLogger("actor")

  def call(self):
    struct = Struct(0, None, [])

    # create actor, and then schedule it
    struct.actor = Actor(name=self._name, queue=self._queue, handler=self._handler)
    struct.actor.schedule()

    return struct
