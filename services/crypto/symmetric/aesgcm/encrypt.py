from cryptography.hazmat.primitives.ciphers import Cipher
from dataclasses import dataclass

import base64
import json
import logging
import os
import typing


@dataclass
class Struct:
    code: int
    encoded: str
    nonce: str
    errors: list[str]


class Encrypt:
    def __init__(self, cipher: typing.Any, data: dict, nonce: bytes = None):
        self._cipher = cipher
        self._data = data
        self._nonce = nonce

        if self._nonce is None:
            self._nonce = os.urandom(12)

        self._data_encoding = "utf-8"
        self._data_bytes = json.dumps(self._data).encode(self._data_encoding)

        self._logger = logging.getLogger("service")

    def call(self):
        struct = Struct(0, "", "", [])

        self._logger.info(f"{__name__} '{self._data}'")

        # encrypt data
        encrypted_bytes = self._cipher.encrypt(self._nonce, self._data_bytes, None)

        # convert encrypted bytes to base64
        struct.encoded = base64.b64encode(encrypted_bytes).decode(self._data_encoding)

        struct.nonce = base64.b64encode(self._nonce).decode(self._data_encoding)

        return struct
