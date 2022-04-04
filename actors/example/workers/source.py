import json
import logging
import typing

from dataclasses import dataclass

from models.actor import Actor
from models.actor_log import ActorLog
from models.actor_message import ActorMessage

@dataclass
class Struct:
  code: int
  errors: list[str]

class WorkerSource:
  def __init__(self, actor: Actor, app_name: str):
    self._actor = actor
    self._app_name = app_name

    self._actor_log = ActorLog(app_name=self._app_name)
    self._logger = logging.getLogger("actor")

  # process kafka msg
  def call(self, msg: ActorMessage) -> Struct:
    struct = Struct(0, [])

    self._logger.info(f"actor '{self._actor.name}' message header {msg.header()}")

    try:
      message_dict = json.loads(msg.value())

      self._logger.info(f"actor '{self._actor.name}' message {message_dict}")

      if self._actor.output is not None:
        # todo: write to output queue
        self._logger.info(f"actor '{self._actor.name}' output todo")

      # append to app log
      log_object = {"actor":self._actor.name, **msg.header()}
      self._actor_log.append(message=log_object)
    except Exception as e:
      struct.code = 500

      self._logger.error(f"actor '{self._actor.name}' exception {e}")

    return struct
