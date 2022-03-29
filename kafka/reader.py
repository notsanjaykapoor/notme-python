from dataclasses import dataclass
import json
import logging

from confluent_kafka import Consumer, KafkaException
from kafka.config import config_reader

@dataclass
class Struct:
  code: int
  errors: list[str]

class KafkaReader:
  def __init__(self, topic: str, group: str, handler):
    self.topic = topic
    self.group = group
    self.handler = handler

    config_reader["group.id"] = self.group

    self.consumer = Consumer(config_reader)
    self.topics = []
    self.logger = logging.getLogger("console")

    self.topics.append(self.topic)

  def call(self):
    struct = Struct(0, [])

    self.logger.info(f"{__name__} starting, topics {self.topics}")

    try:
      self.consumer.subscribe(self.topics)

      while True:
        msg = self.consumer.poll(timeout=1.0)

        if msg is None:
          continue

        if msg.error():
          if msg.error().code() == KafkaError._PARTITION_EOF:
            self.logger.info(f"{__name__} partition eof")
            # todo:
            pass
          elif msg.error():
            raise KafkaException(msg.error())
        else:
          # process message

          if self.handler is not None:
            handler_struct = self.handler.call(msg)

            # check return code and ack
            if handler_struct.code == 0:
              self.logger.info(f"{__name__} ack")
              self.consumer.commit(asynchronous=False)
          else:
              self.logger.info(f"{__name__} no handler ack")
              self.consumer.commit(asynchronous=False)

    except KafkaException as e:
      self.logger.error(f"{__name__} kafka exception {e}")
    except Exception as e:
      self.logger.error(f"{__name__} general exception {e}")
    finally:
      self.consumer.close()
      self.logger.info(f"{__name__} stopping")

    return struct
