from dataclasses import dataclass

import logging
import os
import toml
import typing

from services.crypto.symmetric.aesgcm.load import AesGcmLoad


@dataclass
class Struct:
    code: int
    cipher: typing.Any
    errors: list[str]


class Factory:
    def __init__(self, toml_file: str, user_id: str):
        self._toml_file = toml_file
        self._user_id = user_id

        self.logger = logging.getLogger("service")

    def call(self):
        struct = Struct(0, None, [])

        self.logger.info(f"{__name__}")

        toml_str = toml.load(self._toml_file)
        toml_dict = toml_str[self._user_id]

        cipher_name = toml_dict["cipher"]

        if "aes-gcm" in cipher_name:
            struct_load = AesGcmLoad(key=toml_dict["key"]).call()

            struct.cipher = struct_load.cipher
        else:
            struct.code = 422

        return struct
