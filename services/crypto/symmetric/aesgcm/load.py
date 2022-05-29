from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dataclasses import dataclass

import base64
import logging
import os
import typing


@dataclass
class Struct:
    code: int
    cipher: typing.Any
    errors: list[str]


class AesGcmLoad:
    def __init__(self, key: str):
        self._key = key

        # base64 decode key, and convert to bytes
        self._key_bytes = base64.b64decode(self._key)

        self.logger = logging.getLogger("service")

    def call(self):
        struct = Struct(0, None, [])

        self.logger.info(f"{__name__}")

        # create symmetric key
        struct.cipher = AESGCM(self._key_bytes)

        return struct
