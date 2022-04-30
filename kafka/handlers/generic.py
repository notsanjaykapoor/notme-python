import json
import logging

from dataclasses import dataclass
from typing import Any

@dataclass
class Struct:
  code: int
  errors: list[str]

class HandlerGeneric:
  def __init__(self):
    self.logger = logging.getLogger("console")

  def call(self, msg: Any):
    struct = Struct(0, [])

    try:
      message = json.loads(msg.value())

      self.logger.info(f"{__name__} message {message}")
    except Exception as e:
      struct.code = 500

      self.logger.error(f"{__name__} exception {e}")

    return struct
