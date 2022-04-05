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
      message_object = json.loads(msg.value())

      self._logger.info(f"actor '{self._actor.name}' message {message_object}")

      self._deliver(
        self._process(message_object)
      )

      # append to app log
      log_object = {"actor":self._actor.name, **msg.header()}
      self._actor_log.append(message=log_object)
    except Exception as e:
      struct.code = 500

      self._logger.error(f"actor '{self._actor.name}' exception {e}")

    return struct

  def _process(self, message_object: dict):
    return message_object

  def _deliver(self, message_object: dict) -> int:
    if self._actor.output is None:
      # nothing to do
      return 0

    # add message to actor output queue
    self._actor.output.put_nowait(message_object)

    return 0
