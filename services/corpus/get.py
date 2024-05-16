import dataclasses
import os
import time

import llama_index.core
import llama_index.vector_stores.milvus
import sqlmodel

import services.corpus

@dataclasses.dataclass
class StructNodes:
    code: int
    msec: int
    nodes: list
    errors: list[str]


@dataclasses.dataclass
class StructResponse:
    code: int
    msec: int
    response: str
    errors: list[str]


def get_nodes(db_session: sqlmodel.Session, name_encoded: str, query: str, limit: int) -> StructNodes:
    """
    """
    struct = StructNodes(0, 0, [], [])

    t_start = time.time()

    vector_index = _vector_index(name_encoded=name_encoded)

    retriever = vector_index.as_retriever(similarity_top_k=limit)
    struct.nodes = retriever.retrieve(query)
    struct.msec = (time.time() - t_start) * 1000

    return struct


def get_response(db_session: sqlmodel.Session, name_encoded: str, query: str) -> StructResponse:
    """
    """
    struct = StructResponse(0, 0, "", [])

    t_start = time.time()

    vector_index = _vector_index(name_encoded=name_encoded)

    query_engine = vector_index.as_query_engine()
    struct.response = query_engine.query(query)
    struct.msec = (time.time() - t_start) * 1000

    return struct


def _vector_index(name_encoded: str) -> llama_index.core.VectorStoreIndex:
    parse_result = services.corpus.name_parse(name_encoded=name_encoded)
    model = parse_result.model

    embed_model = services.corpus.embed_model(model=model)
    embed_dims = services.corpus.embed_dims(model=model)

    vector_store = llama_index.vector_stores.milvus.MilvusVectorStore(
        collection_name=name_encoded,
        dim=embed_dims,
        overwrite=False,
        uri=os.environ.get("MILVUS_URL"),
    )
    storage_context = llama_index.core.StorageContext.from_defaults(
        vector_store=vector_store,
    )
    vector_index = llama_index.core.VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
        storage_context=storage_context,
    )

    return vector_index

