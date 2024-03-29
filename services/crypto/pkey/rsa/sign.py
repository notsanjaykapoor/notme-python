import base64
import logging
from dataclasses import dataclass
from typing import Any, Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


@dataclass
class Struct:
    code: int
    encoded: Optional[bytes]
    errors: list[str]


class Sign:
    def __init__(self, private_key: Any, data: str):
        self.private_key = private_key
        self.data = data

        self.data_encoding = "utf-8"
        self.logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, None, [])

        self.logger.info(f"{__name__} data '{self.data}'")

        # convert data str to bytes
        data_bytes = self.data.encode(self.data_encoding)

        # signature is a bytes object whose contents are DER encoded
        signature = self.private_key.sign(
            data_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )

        # create private key
        struct.encoded = base64.b64encode(signature)

        return struct
