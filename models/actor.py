import asyncio
import logging
import typing

class Actor:
  def __init__(self, name: str, queue: asyncio.Queue = None, handler: typing.Any = None, output: asyncio.Queue = None):
    self._name = name
    self._handler = handler
    self._task = None
    self._queue = queue
    self._output = output

    if self._queue is None:
      self._queue = asyncio.Queue(maxsize=0)

    self._logger = logging.getLogger("actor")

  @property
  def handler(self):
    return self._handler

  @handler.setter
  def handler(self, h):
    self._handler = h

  @property
  def name(self):
    return self._name

  @property
  def output(self):
    return self._output

  @output.setter
  def output(self, o):
    self._output = o

  @property
  def queue(self):
    return self._queue

  # actor task default entrypoint
  async def run(self):
    self._logger.info(f"actor '{self._name}' running")

    while True:
      try:
        # block on queue until message is available
        message = await self._queue.get()

        struct = self._handler.call(message=message)

        # ack message
        self._queue.task_done()
      except: # e.g. keyboard interrupt
        self._logger.info(f"actor '{self._name}' exception")
        raise

  # create and schedule actor task
  def schedule(self, task_entry=None):
    self._logger.info(f"actor '{self._name}' scheduling")

    if task_entry:
      self._task = asyncio.create_task(task_entry)
    else:
      self._task = asyncio.create_task(self.run())

  @property
  def task(self):
    return self._task

  @task.setter
  def task(self, t):
    self._task = t
