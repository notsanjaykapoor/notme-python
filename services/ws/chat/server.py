import logging
import sys

from dataclasses import dataclass
from fastapi import WebSocket, WebSocketDisconnect

from context import request_id

from models.socket_manager import SocketManager


@dataclass
class Struct:
    code: int
    errors: list[str]


class Server:
    def __init__(self, socket_manager: SocketManager, ws: WebSocket, user_id: str):
        self._socket_manager = socket_manager
        self._ws = ws
        self._user_id = user_id

        self._logger = logging.getLogger("service")

    async def call(self):
        try:
            await self._ws.accept()

            self._logger.info(f"{__name__} {self._user_id} connected")

            self._socket_manager.connection_add(self._ws, self._user_id)

            while True:
                data = await self._ws.receive_text()

                self._logger.info(f"{__name__} received '{data}'")

                # todo: parse message

                # broadcast message
                await self._socket_manager.broadcast(data, {self._ws})
        except WebSocketDisconnect:
            self._logger.info(f"{__name__} {self._user_id} disconnected")
        except:
            self._logger.info(f"{__name__} exception {sys.exc_info()[0]}")
        finally:
            self._socket_manager.connection_remove(self._ws)
