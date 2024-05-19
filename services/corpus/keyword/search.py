import dataclasses
import os
import time

import llama_index.core
import sqlmodel

@dataclasses.dataclass
class StructNodes:
    code: int
    msec: int
    nodes: list
    errors: list[str]


def search_retrieve(db_session: sqlmodel.Session, name_encoded: str, query: str, limit: int) -> StructNodes:
    """
    """
    struct = StructNodes(0, 0, [], [])

    t_start = time.time()

    keyword_db_path = os.environ.get("KEYWORD_DB_PATH")
    storage_context = llama_index.core.StorageContext.from_defaults(persist_dir=f"{keyword_db_path}/{name_encoded}")
    keyword_index = llama_index.core.load_index_from_storage(storage_context)
    retriever = keyword_index.as_retriever(similarity_top_k=limit, verbose=True)
    struct.nodes = retriever.retrieve(query)

    struct.msec = (time.time() - t_start) * 1000

    return struct
