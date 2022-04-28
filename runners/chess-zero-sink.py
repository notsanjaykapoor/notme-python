from dotenv import load_dotenv

load_dotenv()

import logging
import os
import sys
import ulid
import zmq

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from log import logging_init
from services.zero.sockets.pull import ZeroSocketPull

logger = logging_init("cli")

def chess_zero_sink():
  sink_uri = os.environ.get("CHESS_ZERO_SINK_URI")

  logger.info(f"chess_zero_sink starting")

  struct_socket = ZeroSocketPull(uri=sink_uri, mode="bind").call()
  socket_pull = struct_socket.socket

  dict = {}

  while True:
    object = socket_pull.recv_json()
    name = object["name"]

    match name:
      case "chess-start":
        dict = {}
        logger.info(f"chess_zero_sink start {dict}")

      case "chess-message":
        message = object["message"]

        if not message in dict.keys():
          dict[message] = 0

        dict[message] += 1

        # logger.info(f"chess_zero_sink {dict}")

      case "chess-end":
        logger.info(f"chess_zero_sink end {dict}")

      case _:
        logger.error(f"chess_zero_filter invalid {object}")

if __name__ == "__main__":
  chess_zero_sink()
