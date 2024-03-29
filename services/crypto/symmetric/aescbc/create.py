import logging
import os
import typing
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


@dataclass
class Struct:
    code: int
    cipher: typing.Any
    errors: list[str]


class Create:
    def __init__(self):
        self.logger = logging.getLogger("service")

    def call(self):
        struct = Struct(0, None, [])

        self.logger.info(f"{__name__}")

        key = os.urandom(32)
        iv = os.urandom(16)

        # create symmetric key
        struct.cipher = Cipher(algorithms.AES(key), modes.CBC(iv))

        return struct
