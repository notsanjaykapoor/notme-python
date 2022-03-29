from dataclasses import dataclass
from fastapi import WebSocket, WebSocketDisconnect

import logging

@dataclass
class Struct:
  code: int
  errors: list[str]

class WsReader:
  def __init__(self, ws: WebSocket):
    self.ws = ws

    self.logger = logging.getLogger("service")

  async def call(self):
    struct = Struct(0, [])

    try:
      self.logger.info(f"{__name__}")

      while True:
        data = await self.ws.receive_text()
        self.logger.info(f"{__name__} received '{data}'")
        # await self.ws.send_text(f"message text was: {data}")
    except WebSocketDisconnect:
      self.logger.info(f"{__name__} disconnect")
    except Exception as e:
      struct.code = 500
      self.logger.error(f"{__name__} {e}")

    return struct
