import dataclasses
import os
import re

import sqlmodel

import models
import services.corpus


@dataclasses.dataclass
class Struct:
    code: int
    corpus_map: dict
    source_uris: list[str]
    errors: list[str]


def list_(db_session: sqlmodel.Session, local_dir: str) -> Struct:
    """
    List all directories, and corpuses mapped to their source directories
    """
    struct = Struct(
        code=0,
        corpus_map={},
        source_uris=[],
        errors=[],
    )

    struct.source_uris = sorted([f"file://localhost/{x[0]}" for x in os.walk(local_dir)][1:])

    list_result = services.corpus.list_(db_session=db_session, query="", offset=0, limit=50)
    corpus_list = list_result.objects

    for corpus in corpus_list:
        if corpus.source_uri not in struct.corpus_map:
            struct.corpus_map[corpus.source_uri] = []

        struct.corpus_map[corpus.source_uri].append(corpus)

    return struct

