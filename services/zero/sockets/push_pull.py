import logging
from dataclasses import dataclass

import zmq


@dataclass
class Struct:
    code: int
    socket_push: zmq.Socket
    socket_pull: zmq.Socket
    errors: list[str]


class PushPull:
    def __init__(
        self, uri_push: str, mode_push: str, uri_pull: str, mode_pull: str
    ) -> None:
        self._uri_push = uri_push
        self._mode_push = mode_push
        self._uri_pull = uri_pull
        self._mode_pull = mode_pull

        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, None, None, [])

        struct.socket_push = zmq.Context().socket(zmq.PUSH)

        if self._mode_push == "bind":
            struct.socket_push.bind(self._uri_push)
        elif self._mode_push == "connect":
            struct.socket_push.connect(self._uri_push)
        else:
            raise ValueError("invalid mode")

        struct.socket_pull = zmq.Context().socket(zmq.PULL)

        if self._mode_pull == "bind":
            struct.socket_pull.bind(self._uri_pull)
        elif self._mode_pull == "connect":
            struct.socket_pull.connect(self._uri_pull)
        else:
            raise ValueError("invalid mode")

        self._logger.info(f"{__name__} push {self._uri_push} pull {self._uri_pull}")

        return struct
