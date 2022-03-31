import asyncio
import logging
import typing

class ActorCreate:
  def __init__(self, name: str, queue: asyncio.Queue, handler: typing.Any):
    self.name = name
    self.queue = queue
    self.handler = handler

    self.logger = logging.getLogger("actor")

    self.logger.info(f"{self.name} created")

  def call(self):
    # create_task creates task and schedules it, but does not run it
    return asyncio.create_task(self._run())

  async def _run(self):
    self.logger.info(f"{self.name} starting")

    while True:
      # get message from queue, block if no messages available
      message = await self.queue.get()

      struct = self.handler.call(message)

      # self.logger.info(f"{self.name} message {message}")

      # ack task
      self.queue.task_done()
