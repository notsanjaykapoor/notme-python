from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from dataclasses import dataclass

import base64
import logging
import os
import typing


@dataclass
class Struct:
    code: int
    decoded: str
    errors: list[str]


class Decrypt:
    def __init__(self, cipher: typing.Any, encoded: str, nonce: str):
        self._cipher = cipher
        self._encoded = encoded
        self._nonce = nonce

        self._data_encoding = "utf-8"

        self._data_bytes = base64.b64decode(self._encoded)
        self._nonce_bytes = base64.b64decode(self._nonce)

        self.logger = logging.getLogger("service")

    def call(self):
        struct = Struct(0, "", [])

        # decrypt data
        plaintext_bytes = self._cipher.decrypt(
            self._nonce_bytes, self._data_bytes, None
        )

        # convert decoded bytes to string
        struct.decoded = plaintext_bytes.decode(self._data_encoding)

        self.logger.info(f"{__name__} '{struct.decoded}'")

        return struct
