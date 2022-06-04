from typing import Any


def cipher_name(object: Any) -> str:
    name = type(object).__name__.lower()

    if "aesgcm" in name:
        return "aesgcm"
    else:
        return ""
