from cryptography.hazmat.primitives.asymmetric import ec
from dataclasses import dataclass
from typing import Any, Optional
import logging

@dataclass
class Struct:
  code: int
  key: Any
  errors: list[str]

class Create:
  def __init__(self):
    self.logger = logging.getLogger("console")

  def call(self):
    struct = Struct(0, None, [])

    self.logger.info(f"{__name__}")

    # create private key
    struct.key = ec.generate_private_key(
      ec.SECP384R1()
    )

    return struct
