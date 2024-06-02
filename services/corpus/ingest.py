import dataclasses
import os
import time

import llama_index.core
import llama_index.core.node_parser
import llama_index.storage.docstore.postgres
import llama_index.vector_stores.qdrant
import sqlalchemy
import sqlmodel

import log
import models
import services.corpus
import services.qdrant

@dataclasses.dataclass
class Struct:
    code: int
    corpus: models.Corpus
    seconds: int
    errors: list[str]


KEYWORD_CHUNK_DEFAULT = 1024

VECTOR_CHUNK_SIZE_DEFAULT = 1024
VECTOR_CHUNK_OVERLAP_DEFAULT = 20


def ingest(db_session: sqlmodel.Session, corpus_id: int) -> Struct:
    """
    Load documents, split them into chunks, and generate and store embeddings in a local vector store.
    """
    corpus = services.corpus.get_by_id(db_session=db_session, id=corpus_id)

    struct = Struct(
        code=0,
        corpus=None,
        seconds=0,
        errors=[],
    )

    logger = log.init("app")

    t_start = time.time()

    # initialize corpus state

    corpus.state = models.corpus.STATE_PROCESSING
    db_session.add(corpus)
    db_session.commit()

    storage = {}

    # download corpus source_uri to the local fs

    local_dir, local_files = services.corpus.download(source_uri=corpus.source_uri)
    files_count = len(local_files)
    files_md5 = services.corpus.files_fingerprint(files=local_files)

    logger.info(f"corpus {corpus.id} ingest '{corpus.name}' epoch {corpus.epoch} state '{corpus.state}'")

    torch_device = services.corpus.torch_device()
    model_klass = services.corpus.model_klass(model=corpus.model_name, device=torch_device)
    text_splitter = services.corpus.text_splitter(name=corpus.splitter, model_klass=model_klass)
 
    file_docs = services.corpus.files_docs(files=local_files)
    doc_nodes = text_splitter.get_nodes_from_documents(file_docs)

    docs_count = len(file_docs)
    nodes_count = len(doc_nodes)

    logger.info(f"corpus {corpus.id} ingest '{corpus.name}' epoch {corpus.epoch} state '{corpus.state}' docs {docs_count} nodes {nodes_count}")

    vector_store_name = os.environ.get("VECTOR_STORE")

    if vector_store_name == "faiss":
        logger.info(f"corpus {corpus.id} ingest '{corpus.name}' epoch {corpus.epoch} store 'postgres'")

        # vector index using faiss
        vector_store = llama_index.vector_stores.faiss.FaissVectorStore(faiss_index=faiss.IndexFlatL2(corpus.model_dims))

        vector_storage_context = llama_index.core.StorageContext.from_defaults(
            vector_store=vector_store,
        )

        vector_index = llama_index.core.VectorStoreIndex(
            doc_nodes,
            embed_model=model_klass,
            show_progress=True,
            storage_context=vector_storage_context,
            store_nodes_override=True,
        )

        vector_storage_path = f"{local_dir}/vs"
        vector_storage_uri = f"file://localhost/{local_dir}/vs"

        vector_index.storage_context.persist(
            persist_dir=vector_storage_path,
        )

        storage["vector"] = {
            "store": "faiss",
            "uri": vector_storage_uri,
        }
    elif vector_store_name == "postgres":
        logger.info(f"corpus {corpus.id} ingest '{corpus.name}' epoch {corpus.epoch} store 'postgres'")

        vector_store = llama_index.vector_stores.postgres.PGVectorStore(
            async_connection_string=os.environ.get("DATABASE_VECTOR_URL"),
            connection_string=os.environ.get("DATABASE_VECTOR_URL"),
            schema_name="public",
            table_name="test",
        )
        vector_storage_context = llama_index.core.StorageContext.from_defaults(
            vector_store=vector_store,
        )
        _vector_index = llama_index.core.VectorStoreIndex(
            doc_nodes,
            embed_model=model_klass,
            show_progress=True,
            storage_context=vector_storage_context,
            store_nodes_override=True,
        )

        storage["vector"] = {
            "store": "postgres",
            "uri": "",
        }
    elif vector_store_name == "qdrant":
        logger.info(f"corpus {corpus.id} ingest '{corpus.name}' epoch {corpus.epoch} store 'qdrant'")

        client = services.qdrant.client()

        # delete collection if it exists
        client.delete_collection(corpus.name)

        vector_store = llama_index.vector_stores.qdrant.QdrantVectorStore(
            client=client,
            collection_name=corpus.name,
        )

        vector_storage_context = llama_index.core.StorageContext.from_defaults(
            vector_store=vector_store,
        )

        _vector_index = llama_index.core.VectorStoreIndex(
            doc_nodes,
            embed_model=model_klass,
            show_progress=True,
            storage_context=vector_storage_context,
            store_nodes_override=True,
        )

        storage["vector"] = {
            "store": "qdrant",
            "collection": corpus.name,
        }

    if False:
        # keyword index using postgres

        storage["keyword"] = {
            "name": "postgres",
            "doc_store": f"kw_doc_store_{corpus.id}",
            "idx_store": f"kw_idx_store_{corpus.id}",
        }

        # drop existing keyword indices
        _db_keyword_indices_drop(db_session=db_session, corpus=corpus)

        postgres_doc_store = llama_index.storage.docstore.postgres.PostgresDocumentStore.from_uri(
            perform_setup=True,
            table_name=storage.get("keyword").get("doc_store"),
            uri=os.environ.get("DATABASE_URL"),
        )
        postgres_index_store = llama_index.storage.index_store.postgres.PostgresIndexStore.from_uri(
            perform_setup=True,
            table_name=storage.get("keyword").get("idx_store"),
            uri=os.environ.get("DATABASE_URL"),
        )
        keyword_storage_context = llama_index.core.StorageContext.from_defaults(
            docstore=postgres_doc_store,
            index_store=postgres_index_store,
        )

        keyword_index = llama_index.core.SimpleKeywordTableIndex(
            doc_nodes,
            embed_model=model_klass,
            # keyword_extract_template="KEYWORDS: sanjay,pegmo\n",
            max_keywords_per_chunk=KEYWORD_CHUNK_DEFAULT,
            storage_context=keyword_storage_context,
        )
        keyword_index.storage_context.persist()

    struct.seconds = (time.time() - t_start)

    corpus_meta = {
        "storage": storage,
    }

    # update corpus

    corpus.docs_count = docs_count
    corpus.files_count = files_count
    corpus.meta = corpus.meta | corpus_meta
    corpus.nodes_count = nodes_count
    corpus.fingerprint = files_md5
    corpus.state = models.corpus.STATE_INGESTED

    db_session.add(corpus)
    db_session.commit()

    struct.corpus = corpus

    logger.info(f"corpus {corpus.id} ingest '{corpus.name}' epoch {corpus.epoch} state '{corpus.state}'")

    return struct


def _db_keyword_indices_drop(db_session: sqlmodel.Session, corpus: models.Corpus) -> int:
    """
    """
    for table_name in corpus.storage_keyword_tables:
        db_session.execute(sqlalchemy.text(f"drop table if exists {table_name}"))
    db_session.commit()


def _splitter_name_parse(name: str) -> tuple:
    _, chunk_size, chunk_overlap = name.split(":")

    return int(chunk_size), int(chunk_overlap)
