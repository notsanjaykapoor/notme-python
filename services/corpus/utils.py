import dataclasses
import re

@dataclasses.dataclass
class Struct:
    code: int
    corpus: str
    database: str
    model: str
    errors: list[str]


def name_encode(corpus: str, model: str) -> Struct:
    """
    """
    struct = Struct(0, corpus, "", model, [])

    corpus_normalized = re.sub(": ", "_", corpus.lower())
    model_normalized = re.sub(": ", "_", model.lower())
    struct.database = f"c:{corpus_normalized}:m:{model_normalized}"

    return struct


def name_parse(database: str) -> Struct:
    """
    """
    struct = Struct(0, "", database, "", [])

    match = re.search("^c:([^:]+):m:([^:]+)$", database)

    if not match:
        struct.code = 422
        return struct

    struct.corpus = match[1]
    struct.model = match[2]

    return struct
