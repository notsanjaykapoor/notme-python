#!/usr/bin/env python

import os
import sys

from curio import Channel, run

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import log  # noqa: F401

logger = log.init("api")


async def consumer(ch: Channel):
    c = await ch.connect(authkey=b"curio")

    msg_count = 0
    msg_dict: dict = {}

    while True:
        object = await c.recv()
        name = object["name"]

        match name:
            case "chess-start":
                logger.info(f"consumer {msg_dict}")

            case "chess-end":
                logger.info(f"consumer {msg_dict}")
                break

            case "chess-message":
                # filter message
                message = object["message"]

                if "Result" in message:
                    if not message in msg_dict.keys():
                        msg_dict[message] = 0

                    msg_dict[message] += 1

                msg_count += 1

                if msg_count % 50000 == 0:
                    logger.info(f"consumer {msg_count}")

            case _:
                logger.error(f"consumer invalid {object}")


if __name__ == "__main__":
    ch = Channel(("localhost", 9999))
    run(consumer(ch))
