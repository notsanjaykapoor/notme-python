from dataclasses import dataclass
from typing import Any


def key_type(key: Any) -> str:
    key_name = type(key).__name__.lower()

    if "rsa" in key_name:
        return "rsa"
    elif "ec" in key_name:
        return "ec"
    else:
        return ""
