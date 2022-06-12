import logging
from dataclasses import dataclass

import zmq


@dataclass
class Struct:
    code: int
    socket: zmq.Socket
    errors: list[str]


class Pull:
    def __init__(self, uri: str, mode: str) -> None:
        self._uri = uri
        self._mode = mode

        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, None, [])

        struct.socket = zmq.Context().socket(zmq.PULL)

        if self._mode == "bind":
            struct.socket.bind(self._uri)
        elif self._mode == "connect":
            struct.socket.connect(self._uri)
        else:
            raise ValueError("invalid mode")

        self._logger.info(f"{__name__} uri {self._uri} bound")

        return struct
