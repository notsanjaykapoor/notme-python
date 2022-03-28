from dataclasses import dataclass
import json
import logging

@dataclass
class Struct:
  code: int
  errors: list[str]

class Generic:
  def __init__(self):
    self.logger = logging.getLogger("console")

  def call(self, msg: {}):
    struct = Struct(0, [])

    try:
      message = json.loads(msg.value())

      self.logger.info(f"{__name__} message {message}")
    except Exception as e:
      struct.code = 500

      self.logger.error(f"{__name__} general exception {e}")

    return struct
