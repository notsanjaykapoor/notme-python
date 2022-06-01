#!/usr/local/bin/python3

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import socket
from itertools import cycle

from noise.connection import NoiseConnection

from log import logging_init

logger = logging_init("cli")

if __name__ == "__main__":
    host = "localhost"
    port = int(os.environ["NOISE_SERVER_PORT"])

    logger.info(f"noise server starting {host}:{port}")

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(1)

    while True:
        conn, addr = s.accept()

        logger.info(f"noise server accepted connection from {addr}")

        noise = NoiseConnection.from_name(b"Noise_NN_25519_ChaChaPoly_SHA256")
        noise.set_as_responder()
        noise.start_handshake()

        # Perform handshake. Break when finished
        for action in cycle(["receive", "send"]):
            if noise.handshake_finished:
                break
            elif action == "send":
                ciphertext = noise.write_message()
                conn.sendall(ciphertext)
            elif action == "receive":
                data = conn.recv(2048)
                plaintext = noise.read_message(data)

        # Endless loop "echoing" received data
        while True:
            data = conn.recv(2048)
            if not data:
                break
            received = noise.decrypt(data)
            conn.sendall(noise.encrypt(received))
