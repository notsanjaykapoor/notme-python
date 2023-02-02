from dataclasses import dataclass
import logging

from models.actor import Actor
from models.actor_log import ActorLog
from models.actor_message import ActorMessage


@dataclass
class Struct:
    code: int
    errors: list[str]


class WorkerSource:
    def __init__(self, app_name: str) -> None:
        self._app_name = app_name

        self._dict: dict = {}

        self._actor_log = ActorLog(app_name=self._app_name)
        self._logger = logging.getLogger("actor")

    # process kafka msg
    def call(self, actor: Actor, msg: ActorMessage) -> Struct:
        struct = Struct(0, [])

        self._logger.info(f"actor '{actor.name}' message header {msg.header()}")

        try:
            message_str = msg.value().decode("utf-8")

            self._logger.info(f"actor '{actor.name}' message {message_str}")

            self._process(message_str)

            if "eof" in message_str:
                self._logger.info(f"actor '{actor.name}' totals {self._dict}")

            # self._log_append(actor, msg)
        except Exception as e:
            struct.code = 500

            self._logger.error(f"actor '{actor.name}' exception {e}")

        return struct

    # append to app log
    def _log_append(self, actor: Actor, msg: ActorMessage) -> None:
        self._actor_log.append({"actor": actor.name, **msg.header()})

    def _process(self, message_str: str) -> None:
        message_str_norm = message_str.strip()

        if message_str_norm not in self._dict.keys():
            self._dict[message_str_norm] = 0

        self._dict[message_str_norm] = self._dict[message_str_norm] + 1
