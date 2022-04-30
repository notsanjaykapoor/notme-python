import asyncio
import logging

from dataclasses import dataclass

@dataclass
class Struct:
  code: int
  errors: list[str]

class HandlerGeneric:
  def __init__(self) -> None:
    self._logger = logging.getLogger("actor")

  # called by actor to process a single message
  def call(self, actor_name: str, message: dict) -> Struct:
    struct = Struct(0, [])

    try:
      self._logger.info(f"actor '{actor_name}' message {message}")
    except Exception as e:
      struct.code = 500

      self._logger.error(f"actor '{actor_name}' exception {e}")

    return struct
