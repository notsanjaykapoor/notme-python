import logging
import os
import sys
import ulid

from curio import Channel, run

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from log import logging_init

logger = logging_init("cli")

async def producer(ch: Channel, file: str):
  c = await ch.accept(authkey=b'curio')

  with open(file, mode="r", encoding="ISO-8859-1") as f:
    msg_count = 0

    await c.send({
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

      await c.send(object)

    await c.send({
      "id": ulid.new().str,
      "name": "chess-end",
    })

if __name__ == '__main__':
  ch = Channel(('localhost', 9999))
  file = "./data/chess/mega2400_part_01.pgn.txt"

  run(producer(ch, file))
