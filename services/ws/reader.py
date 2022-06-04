import logging
import sys

from dataclasses import dataclass
from fastapi import WebSocket, WebSocketDisconnect

from context import request_id


@dataclass
class Struct:
    code: int
    errors: list[str]


class Reader:
    def __init__(self, ws: WebSocket):
        self._ws = ws

        self._logger = logging.getLogger("service")

    async def call(self):
        struct = Struct(0, [])

        try:
            self._logger.info(f"{request_id.get()} {__name__} waiting")

            while True:
                data = await self._ws.receive_text()
                self._logger.info(f"{request_id.get()} {__name__} received '{data}'")
        except WebSocketDisconnect:
            self._logger.info(f"{request_id.get()} {__name__} disconnect")
        except:
            struct.code = 500
            self._logger.error(
                f"{request_id.get()} {__name__} exception {sys.exc_info()[0]}"
            )

        return struct
