import logging

from dataclasses import dataclass

from models.actor import Actor
from models.actor_log import ActorLog


@dataclass
class Struct:
    code: int
    errors: list[str]


class WorkerEcho:
    def __init__(self, app_name: str):
        self._app_name = app_name

        self._actor_log = ActorLog(app_name=self._app_name)
        self._logger = logging.getLogger("actor")

    # process task message
    def call(self, actor: Actor, message: dict):
        struct = Struct(0, [])

        try:
            self._logger.info(f"actor '{actor.name}' message {message}")
        except:
            struct.code = 500

            self._logger.error(f"actor '{actor.name}' exception")

        return struct

    def _deliver(self, actor: Actor, message_object: dict) -> int:
        if self._actor.output is None:
            # nothing to do
            return 0

        # add message to actor output queue
        actor.output.put_nowait(message_object)

        return 0
