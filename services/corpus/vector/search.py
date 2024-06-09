import dataclasses
import os
import time

import llama_index.core
import  llama_index.core.indices
import llama_index.core.storage.docstore
import llama_index.vector_stores.qdrant
import qdrant_client
import sqlmodel

import context
import log
import models
import services.corpus
import services.corpus.fs
import services.corpus.models


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


logger = log.init("api")


def search_augment(db_session: sqlmodel.Session, corpus: models.Corpus, query: str) -> StructResponse:
    """
    """
    struct = StructResponse(0, 0, "", [])

    t_start = time.time()

    vector_index = _vector_index(db_session=db_session, corpus=corpus)
    query_engine = vector_index.as_query_engine()
    struct.response = query_engine.query(query)

    struct.msec = (time.time() - t_start) * 1000

    return struct


def search_retrieve(db_session: sqlmodel.Session, corpus: models.Corpus, query: str, limit: int) -> StructNodes:
    """
    """
    struct = StructNodes(0, 0, [], [])

    t_start = time.time()

    vector_index = _vector_index(db_session=db_session, corpus=corpus)
    retriever = vector_index.as_retriever(similarity_top_k=limit, image_similarity_top_k=limit)
    struct.nodes = retriever.retrieve(query)

    for node in struct.nodes:
        print(node) # xxx

    struct.msec = (time.time() - t_start) * 1000

    return struct


def _vector_index(db_session: sqlmodel.Session, corpus: models.Corpus) -> llama_index.core.VectorStoreIndex:
    """
    Load vector index
    """
    torch_device = services.corpus.torch_device()
    model_klass = services.corpus.models.resolve(model=corpus.model_name, device=torch_device)

    vector_store_name = os.environ.get("VECTOR_STORE")

    if vector_store_name == "faiss":
        import faiss #

        vector_storage_uri = corpus.storage_meta.get("vector").get("uri")
        _, _, vector_storage_path = services.corpus.fs.source_uri_parse(source_uri=vector_storage_uri)

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

        logger.info(
            f"{context.rid_get()} corpus '{corpus.name}' model '{corpus.model_name}' load - text '{corpus.vector_txt_uri}' image '{corpus.vector_img_uri}'"
        )

        if corpus.vector_txt_uri:
            vector_txt_name = corpus.vector_txt_uri.split(":")[-1]

            vector_store = llama_index.vector_stores.qdrant.QdrantVectorStore(
                client=client,
                collection_name=vector_txt_name,
            )
        else:
            vector_store = None # invalid case?

        if corpus.vector_img_uri:
            vector_img_name = corpus.vector_img_uri.split(":")[-1]
            image_store = llama_index.vector_stores.qdrant.QdrantVectorStore(
                client=client,
                collection_name=vector_img_name,
            )
        else:
            image_store = None

        storage_context = llama_index.core.StorageContext.from_defaults(
            vector_store=vector_store,
            image_store=image_store,
        )

        if image_store:
            # multi modal index always requires a valid vector store
            # vector_index = llama_index.core.indices.MultiModalVectorStoreIndex.from_vector_store(
            #     embed_model=model_klass,
            #     image_store=image_store,
            #     vector_store=vector_store,
            #     # storage_context=storage_context, # using this generates 'got multiple values for keyword argument 'storage_context''
            # )
            vector_index = llama_index.core.VectorStoreIndex.from_vector_store(
                embed_model=model_klass,
                image_store=image_store,
                storage_context=storage_context,
                vector_store=vector_store,
            )
        else:
            vector_index = llama_index.core.VectorStoreIndex.from_vector_store(
                embed_model=model_klass,
                storage_context=storage_context,
                vector_store=vector_store,
            )

    return vector_index

