import logging

from dataclasses import dataclass

from models.actor import Actor
from models.actor_log import ActorLog


@dataclass
class Struct:
    code: int
    errors: list[str]


class WorkerEcho:
    def __init__(self, actor: Actor, app_name: str):
        self._actor = actor
        self._app_name = app_name

        self._actor_log = ActorLog(app_name=self._app_name)
        self._logger = logging.getLogger("actor")

    # process task message
    def call(self, message: dict):
        struct = Struct(0, [])

        try:
            self._logger.info(f"actor '{self._actor.name}' message {message}")
        except:
            struct.code = 500

            self._logger.error(f"actor '{self._actor.name}' exception")

        return struct

    def _deliver(self, message_object: dict) -> int:
        if self._actor.output is None:
            # nothing to do
            return 0

        # add message to actor output queue
        self._actor.output.put_nowait(message_object)

        return 0
