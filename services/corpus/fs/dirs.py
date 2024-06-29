import dataclasses
import os

import sqlmodel

import services.corpus


@dataclasses.dataclass
class Struct:
    code: int
    corpus_map: dict
    dirs_map: dict
    source_uris: list[str]
    errors: list[str]


def dirs(db_session: sqlmodel.Session, local_dir: str, dir_type: str, query: str, offset: int, limit: int) -> Struct:
    """
    List all directories, with corpuses mapped to their source directories
    """
    struct = Struct(
        code=0,
        corpus_map={}, # map source_uri to corpus
        dirs_map={}, # map source_uri without a corpus
        source_uris=[],
        errors=[],
    )

    for root, dir, files in  os.walk(local_dir):
        if dir_type == "leaf" and len(dir):
            # ignore non-leaf directories
            continue

        if len(files) and _path_match(path=root, query=query) == 0:
            # directory has at least 1 file
            struct.source_uris.append(f"file://localhost/{root}")

    list_result = services.corpus.list(db_session=db_session, query="", offset=offset, limit=limit)
    corpus_list = list_result.objects

    # map source_uri to related corpus
    for corpus in corpus_list:
        if corpus.source_uri not in struct.corpus_map:
            struct.corpus_map[corpus.source_uri] = []

        struct.corpus_map[corpus.source_uri].append(corpus)

    # map dirs without a corpus
    struct.dirs_map = {uri:{} for uri in (set(struct.source_uris) - set(struct.corpus_map.keys()))}

    return struct


def _path_match(path: str, query: str) -> int:
    if not query:
        return 0
    
    if query in path:
        return 0
    
    return 1