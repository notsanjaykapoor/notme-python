from dataclasses import dataclass
import json
import logging

from confluent_kafka import Producer
from kafka.config import config_writer

@dataclass
class Struct:
  code: int
  errors: list[str]

class Writer:
  def __init__(self, topic: str, message: {}):
    self.topic = topic
    self.message = message

    self.producer = Producer(config_writer)
    self.logger = logging.getLogger("console")

  def call(self):
    struct = Struct(0, [])

    json_str = json.dumps(self.message)

    self.logger.info(f"{__name__} topic {self.topic} message {json_str}")

    self.producer.produce(self.topic, key="message", value=json_str)
    self.producer.flush()

    return struct
