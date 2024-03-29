import logging
import typing
from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric import ec


@dataclass
class Struct:
    code: int
    key: typing.Any
    errors: list[str]


class Create:
    def __init__(self):
        self.logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, None, [])

        self.logger.info(f"{__name__}")

        # create private key
        struct.key = ec.generate_private_key(ec.SECP384R1())

        return struct
