import dataclasses
import os
import re

import sqlmodel

import models
import services.corpus


@dataclasses.dataclass
class Struct:
    code: int
    corpuses: list[dict]
    errors: list[str]


def list_(db_session: sqlmodel.Session, dir: str) -> Struct:
    """
    List all directories with corpus state
    """
    struct = Struct(0, [], [])

    list_result = services.corpus.list_(db_session=db_session, query="", offset=0, limit=50)
    corpus_list = list_result.objects
    corpus_map = {corpus.source_dir:corpus for corpus in corpus_list}

    source_dirs = sorted([x[0] for x in os.walk(dir)][1:])

    for source_dir in source_dirs:
        corpus = corpus_map.get(source_dir)

        if not corpus:
            corpus = models.Corpus(
                name="",
                source_dir=source_dir,
                state="new",
            )

        struct.corpuses.append(corpus)

    return struct

