import logging
import sys
import typing
from dataclasses import dataclass

from fastapi import WebSocket


class SocketManager:
    def __init__(self):
        self._connections = {}
        self._logger = logging.getLogger("service")

    async def broadcast(self, message: str, exclude: set[typing.Any]):
        connections = self._broadcast_set(exclude)

        for connection in connections:
            await connection.send_text(message)

    def connection_add(self, ws: WebSocket, user_id: str):
        self._connections[ws] = user_id

    def connection_remove(self, ws: WebSocket):
        self._connections.pop(ws, None)

    def count(self):
        return len(self._connections)

    def users(self):
        return self._connections.values()

    def _broadcast_set(self, exclude: set[typing.Any]):
        return set(self._connections.keys()) - exclude
