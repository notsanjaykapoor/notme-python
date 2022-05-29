from cryptography.hazmat.primitives.asymmetric import ec
from dataclasses import dataclass

import logging
import typing


@dataclass
class Struct:
    code: int
    key: typing.Any
    errors: list[str]


class PkeyCreate:
    def __init__(self):
        self.logger = logging.getLogger("service")

    def call(self):
        struct = Struct(0, None, [])

        self.logger.info(f"{__name__}")

        # create private key
        struct.key = ec.generate_private_key(ec.SECP384R1())

        return struct
