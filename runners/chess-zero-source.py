from dotenv import load_dotenv

load_dotenv()

import logging
import os
import sys
import ulid
import zmq

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from log import logging_init
from services.zero.sockets.push import ZeroSocketPush

logger = logging_init("cli")

def chess_zero_source(file: str):
  filter_uri: str = os.environ.get("CHESS_ZERO_FILTER_URI", "")

  if not filter_uri:
    raise ValueError("missing uri")

  logger.info(f"chess_zero_source starting")

  struct_socket = ZeroSocketPush(uri=filter_uri, mode="bind").call()
  socket_push = struct_socket.socket

  with open(file, mode="r", encoding="ISO-8859-1") as f:
    msg_count = 0

    socket_push.send_json({
      "id": ulid.new().str,
      "name": "chess-start",
    })

    for line in f:
      object = {
        "id": ulid.new().str,
        "name": "chess-message",
        "message": line.strip(),
      }

      logger.info(f"{object}")

      socket_push.send_json(object)

      msg_count += 1

    socket_push.send_json({
      "id": ulid.new().str,
      "name": "chess-end",
    })

    logger.info(f"chess_zero_source message count {msg_count}")

if __name__ == "__main__":
  chess_zero_source(file="./data/chess/mega2400_part_01.pgn.txt")
