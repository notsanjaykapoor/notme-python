from dataclasses import dataclass

import asyncio
import logging

@dataclass
class Struct:
  code: int
  errors: list[str]

class HandlerGeneric:
  def __init__(self):
    self._logger = logging.getLogger("actor")

  def call(self, actor_name: str, message: dict):
    struct = Struct(0, [])

    try:
      self._logger.info(f"actor '{actor_name}' message {message}")
    except Exception as e:
      struct.code = 500

      self._logger.error(f"actor '{actor_name}' exception {e}")

    return struct
