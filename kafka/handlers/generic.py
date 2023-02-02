import dataclasses
import json

import kafka
import log
from models.actor import Actor
from models.actor_message import ActorMessage


@dataclasses.dataclass
class Struct:
    code: int
    errors: list[str]


class Generic(kafka.Handler):
    def __init__(self):
        self._logger = log.init("service")

    def call(self, actor: Actor, msg: ActorMessage) -> Struct:
        struct = Struct(0, [])

        try:
            message = json.loads(msg.value())

            self._logger.info(f"{__name__} message {message}")
        except Exception as e:
            struct.code = 500

            self._logger.error(f"{__name__} exception {e}")

        return struct
