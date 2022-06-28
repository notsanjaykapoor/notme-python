#!/usr/bin/env python

from dotenv import load_dotenv

load_dotenv()

import logging
import os
import sys

import ulid
import zmq

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import log
import services.zero.sockets

logger = log.init("api")


def chess_zero_filter():
    filter_uri = os.environ.get("CHESS_ZERO_FILTER_URI")
    sink_uri = os.environ.get("CHESS_ZERO_SINK_URI")

    logger.info(f"chess_zero_filter starting")

    struct_socket = services.zero.sockets.PushPull(
        uri_pull=filter_uri,
        mode_pull="connect",
        uri_push=sink_uri,
        mode_push="connect",
    ).call()

    socket_pull = struct_socket.socket_pull
    socket_push = struct_socket.socket_push

    msg_count = 0

    while True:
        object = socket_pull.recv_json()
        name = object["name"]

        match name:
            case "chess-start" | "chess-end":
                # forward message
                socket_push.send_json(object)

                logger.info(f"chess_zero_filter {object}")

            case "chess-message":
                # filter message
                message = object["message"]

                if "Result" in message:
                    socket_push.send_json(object)

                msg_count += 1

                if msg_count % 100000 == 0:
                    logger.info(f"chess_zero_filter {msg_count}")

            case _:
                logger.error(f"chess_zero_filter invalid {object}")


if __name__ == "__main__":
    chess_zero_filter()
