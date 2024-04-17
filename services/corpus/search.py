import dataclasses
import os


@dataclasses.dataclass
class Struct:
    code: int
    names: list[str]
    errors: list[str]


DIR_ROOT = "./faiss"

def search(query: str) -> Struct:
    struct = Struct(0, [], [])

    struct.names = sorted(os.listdir(DIR_ROOT))

    return struct