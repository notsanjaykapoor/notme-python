from dataclasses import dataclass

import asyncio
import logging
import typing

@dataclass
class Struct:
  code: int
  task: asyncio.Task
  errors: list[str]

class ActorCreate:
  def __init__(self, name: str, handler: typing.Any):
    self._name = name
    self._handler = handler
    self._task = None

    self._queue = asyncio.Queue(maxsize=0)
    self._logger = logging.getLogger("actor")

  def call(self):
    struct = Struct(0, None, [])

    self._logger.info(f"actor '{self._name}' call")

    # create task and schedule it
    struct.task = self._task = asyncio.create_task(self._run())

    return struct

  async def _run(self):
    self._logger.info(f"actor '{self._name}' starting")

    while True:
      # block on queue until message is available
      message = await self._queue.get()

      struct = self._handler.call(
        actor_name=self._name,
        message=message,
      )

      # ack task
      self._queue.task_done()


  @property
  def name(self):
    return self._name

  @property
  def queue(self):
    return self._queue

  @property
  def task(self):
    return self._task
