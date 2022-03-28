from dataclasses import dataclass
import json

from confluent_kafka import Producer
from kafka.config import config

@dataclass
class Struct:
  code: int
  errors: list[str]

class Writer:
  def __init__(self, topic: str, message: {}):
    self.topic = topic
    self.message = message

    self.producer = Producer(config)

  def call(self):
    struct = Struct(0, [])

    json_str = json.dumps(self.message)

    print(f"topic {self.topic} message {json_str} write")

    self.producer.produce(self.topic, key="message", value=json_str)
    self.producer.flush()

    return struct
