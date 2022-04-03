import asyncio
import json
import logging
import typing

from dataclasses import dataclass

from kafka.handlers.generic import HandlerGeneric as KafkaHandler
from kafka.reader import KafkaReader

from models.actor import Actor

@dataclass
class Struct:
  code: int
  actor: Actor
  errors: list[str]

class ActorSource:
  def __init__(self, name: str, topic: str, group: str, handler: typing.Any = None):
    self._name = name
    self._topic = topic
    self._group = group
    self._handler = handler

    if self._handler is None:
      self._handler = KafkaHandler()

    self._actor = None
    self._reader = None
    self._logger = logging.getLogger("actor")

  def call(self):
    struct = Struct(0, None, [])

    # create actor, and then schedule it using the source run method as the task entrypoint
    self._actor = Actor(name=self._name)
    self._actor.schedule(task_entry=self.run())

    struct.actor = self._actor

    return struct

  # actor task entrypoint
  async def run(self):
    self._logger.info(f"actor '{self._actor.name}' running")

    try:
      # read from kafka stream
      self._reader = KafkaReader(self._topic, self._group, self._handler)
      self._reader.call()

      self._logger.info(f"actor exiting")
    except: # e.g. keyboard interrupt
      self._logger.info(f"actor '{self._actor.name}' exception")
    finally:
      self._logger.info(f"actor '{self._actor.name}' exiting")
