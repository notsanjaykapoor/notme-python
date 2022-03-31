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

class SymmetricDecrypt:
  def __init__(self, cipher: typing.Any, encoded: str):
    self.cipher = cipher
    self.encoded = encoded

    self.data_encoding = "utf-8"
    self.logger = logging.getLogger("service")

  def call(self):
    struct = Struct(0, "", [])

    decryptor = self.cipher.decryptor()

    # convert str to bytes
    data_bytes = base64.b64decode(self.encoded)

    # decrypt data
    decoded_byted = decryptor.update(data_bytes) + decryptor.finalize()

    # convert decoded bytes to string
    struct.decoded = decoded_byted.decode(self.data_encoding)

    self.logger.info(f"{__name__} '{struct.decoded}'")

    return struct
