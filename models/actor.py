import asyncio
import logging
import sys
import typing

from kafka.handlers.generic import HandlerGeneric as KafkaHandler
from kafka.reader import KafkaReader

class Actor:
  def __init__(self, name: str, queue: asyncio.Queue = None, topic: str = None, group: str = None, output: asyncio.Queue = None):
    self._name = name
    self._queue = queue
    self._topic = topic
    self._group = group
    self._output = output

    self._task = None
    self._handler = None

    if self._topic is not None and self._queue is not None:
      raise ValueError("invalid args")

    if self._topic is None and self._queue is None:
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

  # create and schedule actor task
  def schedule(self, task_entry=None) -> int:
    self._logger.info(f"actor '{self._name}' scheduling")

    if self._handler is None:
      raise ValueError("handler missing")

    if task_entry is not None:
      self._task = asyncio.create_task(task_entry, name=self._name)
    elif self._topic is not None:
      self._logger.info(f"actor '{self._name}' scheduling kafka")
      self._task = asyncio.create_task(self._wait_kafka_queue(), name=self._name)
    else:
      self._logger.info(f"actor '{self._name}' scheduling task")
      self._task = asyncio.create_task(self._wait_task_queue(), name=self._name)

    return 0

  async def _wait_kafka_queue(self):
    self._logger.info(f"actor '{self._name}' running")

    try:
      # read from kafka stream
      self._reader = KafkaReader(self._topic, self._group, self._handler)
      await self._reader.call()

      self._logger.info(f"actor '{self._name}' exiting")
    except: # e.g. keyboard interrupt
      self._logger.info(f"actor '{self._name}' kafka exception {sys.exc_info()[0]}")
    finally:
      self._logger.info(f"actor '{self._name}' exiting")

  async def _wait_task_queue(self):
    self._logger.info(f"actor '{self._name}' running")

    try:
      while True:
        # block on queue until message is available
        message = await self._queue.get()

        struct = self._handler.call(message=message)

        # ack message
        self._queue.task_done()
    except: # e.g. keyboard interrupt
      self._logger.info(f"actor '{self._name}' task exception {sys.exc_info()[0]}")
      raise

  @property
  def task(self):
    return self._task

  @task.setter
  def task(self, t):
    self._task = t
