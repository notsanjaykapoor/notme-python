import asyncio
import json
import logging
import typing

from dataclasses import dataclass

from confluent_kafka import Consumer, KafkaError, KafkaException
from kafka.config import config_reader

from models.actor_message import ActorMessage

@dataclass
class Struct:
  code: int
  errors: list[str]

class KafkaReader:
  def __init__(self, topic: str, group: str, handler: typing.Any):
    self._topic = topic
    self._group = group
    self._handler = handler

    config_reader["group.id"] = self._group

    self._consumer = Consumer(config_reader)
    self._topics = []
    self._logger = logging.getLogger("service")
    self._task = asyncio.current_task()

    self._topics.append(self._topic)

    if self._task is not None:
      self._log_subject = f"actor '{self._task.get_name()}' {__name__}"
    else:
      self._log_subject = f"{__name__}"

  def call(self):
    struct = Struct(0, [])

    self._logger.info(f"{self._log_subject} reading topics {self._topics}")

    try:
      self._consumer.subscribe(self._topics)

      while True:
        msg = self._consumer.poll(timeout=1.0)

        if msg is None:
          continue

        if msg.error():
          # whoops, some type of read error
          if msg.error().code() == KafkaError._PARTITION_EOF:
            self._logger.info(f"{self._log_subject} partition eof")
            # todo:
            pass
          elif msg.error():
            raise KafkaException(msg.error())
        else:
          # call handler to process message
          handler_struct = self._handler.call(ActorMessage(msg))

          # check return code and ack
          if handler_struct.code == 0:
            self._logger.info(f"{self._log_subject} ack")
            self._consumer.commit(asynchronous=False)

    except KafkaException as e:
      self._logger.error(f"{self._log_subject} kafka exception {e}")
    except Exception as e:
      self._logger.error(f"{self._log_subject} exception {e}")
    except: # e.g. keyboard interrupt
      self._logger.error(f"{self._log_subject} exception")
      raise
    finally:
      self._consumer.close()
      self._logger.info(f"{self._log_subject} stopping")

    return struct
