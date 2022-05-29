from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from dataclasses import dataclass

import base64
import logging
import os
import typing


@dataclass
class Struct:
    code: int
    encoded: str
    errors: list[str]


class AesCbcEncrypt:
    def __init__(self, cipher: typing.Any, data: str):
        self.cipher = cipher
        self.data = data

        self.data_encoding = "utf-8"
        self.logger = logging.getLogger("service")

    def call(self):
        struct = Struct(0, "", [])

        self.logger.info(f"{__name__} '{self.data}'")

        encryptor = self.cipher.encryptor()

        # convert str to bytes
        data_bytes = self.data.encode(self.data_encoding)

        # encrypt data
        encrypted_bytes = encryptor.update(data_bytes) + encryptor.finalize()

        # convert encrypted bytes to base64
        struct.encoded = base64.b64encode(encrypted_bytes)

        return struct
