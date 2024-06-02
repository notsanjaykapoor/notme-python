import dataclasses
import os
import time

import llama_index.core
import llama_index.core.storage.docstore
import llama_index.vector_stores.qdrant
import qdrant_client
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


def search_augment(db_session: sqlmodel.Session, name_encoded: str, query: str) -> StructResponse:
    """
    """
    struct = StructResponse(0, 0, "", [])

    t_start = time.time()

    vector_index = _vector_index(db_session=db_session, name_encoded=name_encoded)
    query_engine = vector_index.as_query_engine()
    struct.response = query_engine.query(query)

    struct.msec = (time.time() - t_start) * 1000

    return struct


def search_retrieve(db_session: sqlmodel.Session, name_encoded: str, query: str, limit: int) -> StructNodes:
    """
    """
    struct = StructNodes(0, 0, [], [])

    t_start = time.time()

    vector_index = _vector_index(db_session=db_session, name_encoded=name_encoded)
    retriever = vector_index.as_retriever(similarity_top_k=limit)
    struct.nodes = retriever.retrieve(query)

    struct.msec = (time.time() - t_start) * 1000

    return struct


def _vector_index(db_session: sqlmodel.Session, name_encoded: str) -> llama_index.core.VectorStoreIndex:
    """
    Load vector index
    """
    corpus = services.corpus.get_by_name(db_session=db_session, name=name_encoded)

    if not corpus:
        raise f"invalid corpus {name_encoded}"
    
    torch_device = services.corpus.torch_device()
    model_klass = services.corpus.model_klass(model=corpus.model_name, device=torch_device)
    _model_dims = services.corpus.model_dims(model=corpus.model_name)

    vector_store_name = os.environ.get("VECTOR_STORE")

    if vector_store_name == "faiss":
        import faiss #

        vector_storage_uri = corpus.storage_meta.get("vector").get("uri")
        _, _, vector_storage_path = services.corpus.source_uri_parse(source_uri=vector_storage_uri)

        vector_store = llama_index.vector_stores.faiss.FaissVectorStore.from_persist_dir(
            persist_dir=vector_storage_path
        )

        doc_store = llama_index.core.storage.docstore.SimpleDocumentStore.from_persist_dir(
            persist_dir=vector_storage_path
        )

        storage_context = llama_index.core.StorageContext.from_defaults(
            docstore=doc_store,
            vector_store=vector_store,
            persist_dir=vector_storage_path,
        )

        vector_index = llama_index.core.VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=model_klass,
            storage_context=storage_context,
        )
    elif vector_store_name == "postgres":
        vector_store = llama_index.vector_stores.postgres.PGVectorStore(
        )
    elif vector_store_name == "qdrant":
        client = qdrant_client.QdrantClient(url=os.environ.get("QDRANT_URL"))

        vector_store = llama_index.vector_stores.qdrant.QdrantVectorStore(
            client=client,
            collection_name=corpus.name,
        )

        storage_context = llama_index.core.StorageContext.from_defaults(
            vector_store=vector_store,
        )

        vector_index = llama_index.core.VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=model_klass,
            storage_context=storage_context,
        )

    return vector_index

