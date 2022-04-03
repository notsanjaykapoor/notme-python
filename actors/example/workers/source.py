import json
import logging
import typing

from dataclasses import dataclass

@dataclass
class Struct:
  code: int
  errors: list[str]

class WorkerSource:
  def __init__(self, actor_name: str):
    self._actor_name = actor_name

    self._logger = logging.getLogger("actor")

  # process kafka msg
  def call(self, msg: typing.Any):
    struct = Struct(0, [])

    try:
      message = json.loads(msg.value())

      self._logger.info(f"actor '{self._actor_name}' message {message}")
    except Exception as e:
      struct.code = 500

      self._logger.error(f"actor '{self._actor_name}' exception {e}")

    return struct
