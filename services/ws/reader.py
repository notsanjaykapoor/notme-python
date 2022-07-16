import dataclasses
import logging
import sys

from fastapi import WebSocket, WebSocketDisconnect

import context


@dataclasses.dataclass
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
            self._logger.info(f"{context.rid_get()} {__name__} waiting")

            while True:
                data = await self._ws.receive_text()
                self._logger.info(f"{context.rid_get()} {__name__} received '{data}'")
        except WebSocketDisconnect:
            self._logger.info(f"{context.rid_get()} {__name__} disconnect")
        except Exception as e:
            struct.code = 500
            self._logger.error(f"{context.rid_get()} {__name__} exception {e}")

        return struct
