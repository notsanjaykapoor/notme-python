import dataclasses
import os

import llama_index.core
import llama_index.vector_stores.milvus

import  services.corpus

@dataclasses.dataclass
class StructNodes:
    code: int
    nodes: list
    errors: list[str]


@dataclasses.dataclass
class StructResponse:
    code: int
    response: str
    errors: list[str]


def get_nodes(name_encoded: str, query: str, limit: int) -> StructNodes:
    """
    """
    struct = StructNodes(0, [], [])

    vector_index = _vector_index(name_encoded=name_encoded)

    retriever = vector_index.as_retriever(similarity_top_k=limit)
    struct.nodes = retriever.retrieve(query)

    return struct


def get_response(name_encoded: str, query: str) -> StructResponse:
    """
    """
    struct = StructResponse(0, "", [])

    vector_index = _vector_index(name_encoded=name_encoded)

    query_engine = vector_index.as_query_engine()
    struct.response = query_engine.query(query)

    return struct


def _vector_index(name_encoded: str) -> llama_index.core.VectorStoreIndex:
    parse_result = services.corpus.name_parse(name_encoded=name_encoded)
    model = parse_result.model

    model_embeddings = services.corpus.model_embeddings(model=model)
    model_dimensions = services.corpus.model_dimensions(model=model)

    vector_store = llama_index.vector_stores.milvus.MilvusVectorStore(
        collection_name=name_encoded,
        dim=model_dimensions,
        overwrite=False,
        uri=os.environ.get("MILVUS_URL"),
    )
    storage_context = llama_index.core.StorageContext.from_defaults(
        vector_store=vector_store,
    )
    vector_index = llama_index.core.VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=model_embeddings,
        storage_context=storage_context,
    )

    return vector_index

