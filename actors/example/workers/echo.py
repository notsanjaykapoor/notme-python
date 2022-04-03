import logging

from dataclasses import dataclass

@dataclass
class Struct:
  code: int
  errors: list[str]

class WorkerEcho:
  def __init__(self, actor_name: str):
    self._actor_name = actor_name

    self._logger = logging.getLogger("actor")

  # called by actor to process a single message
  def call(self, message: dict):
    struct = Struct(0, [])

    try:
      self._logger.info(f"actor '{self._actor_name}' message {message}")
    except:
      struct.code = 500

      self._logger.error(f"actor '{self._actor_name}' exception")

    return struct
