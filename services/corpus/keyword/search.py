import dataclasses
import os
import time

import llama_index.core
import llama_index.storage.docstore.postgres
import llama_index.storage.index_store.postgres
import sqlmodel

import services.corpus

@dataclasses.dataclass
class StructNodes:
    code: int
    msec: int
    nodes: list
    errors: list[str]


# note: not used in current implementation
def search(db_session: sqlmodel.Session, name_encoded: str, query: str, limit: int) -> StructNodes:
    """
    """
    struct = StructNodes(0, 0, [], [])

    t_start = time.time()

    corpus = services.corpus.get_by_name(db_session=db_session, name=name_encoded)

    # build storage context from existing postgres keyword indices

    keyword_storage = corpus.storage_keyword

    postgres_doc_store = llama_index.storage.docstore.postgres.PostgresDocumentStore.from_uri(
        perform_setup=False,
        table_name=keyword_storage.get("doc_store"),
        uri=os.environ.get("DATABASE_URL"),
    )
    postgres_index_store = llama_index.storage.index_store.postgres.PostgresIndexStore.from_uri(
        perform_setup=True,
        table_name=keyword_storage.get("idx_store"),
        uri=os.environ.get("DATABASE_URL"),
    )
    keyword_storage_context = llama_index.core.StorageContext.from_defaults(
        docstore=postgres_doc_store,
        index_store=postgres_index_store,
    )

    # load index and execute query

    keyword_index = llama_index.core.load_index_from_storage(
        storage_context=keyword_storage_context,
    )
    retriever = keyword_index.as_retriever(similarity_top_k=limit, verbose=True)
    struct.nodes = retriever.retrieve(query)

    struct.msec = (time.time() - t_start) * 1000

    return struct
