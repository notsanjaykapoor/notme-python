from dataclasses import dataclass

import aioconsole
import asyncio
import logging
import sys
import typing
import websockets

@dataclass
class Struct:
  code: int
  errors: list[str]

class IoConsoleSocket:
  def __init__(self, user_id: str, ws: websockets.WebSocketClientProtocol):
    self._user_id = user_id
    self._ws = ws

    self._prompt = ""
    self._wait_seconds = 0.5
    self._logger = logging.getLogger("service")

  async def call(self):
    struct = Struct(0, [])

    await self._ws.send(f"{self._user_id}: joined")

    while True:
      # check socket
      socket_data = await self._socket(self._wait_seconds)

      if socket_data is not None:
        # console print
        print(socket_data)

      # check console
      console_data = await self._console(self._wait_seconds)

      if console_data is not None:
        if "/exit" in console_data or "/quit" in console_data:
          # send leaving message and then exit
          await self._ws.send(f"{self._user_id}: leaving")
          break
        else:
          # send to chat server
          await self._ws.send(f"{self._user_id}: {console_data}")

    return struct

  # check console for input
  async def _console(self, timeout_seconds: int):
    try:
      cmd = await asyncio.wait_for(
        aioconsole.ainput(self._prompt),
        timeout_seconds,
      )

      return cmd
    except asyncio.TimeoutError:
      return None
    except:
      self._logger.info(f"{__name__} console exception {sys.exc_info()[0]}")
      raise

  # check socket for message
  async def _socket(self, timeout_seconds):
    try:
      data = await asyncio.wait_for(
        self._ws.recv(),
        timeout_seconds,
      )

      return data
    except asyncio.TimeoutError:
      return None
    except websockets.exceptions.ConnectionClosedError:
      self._logger.info(f"{__name__} socket closed")
      raise
    except:
      self._logger.error(f"{__name__} socket exception {sys.exc_info()[0]}")
      raise
