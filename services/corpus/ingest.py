import dataclasses
import hashlib
import os
import time

import llama_index.core
import llama_index.core.ingestion
import llama_index.core.node_parser
import llama_index.embeddings
import llama_index.readers.file
import llama_index.readers.web
import llama_index.storage.docstore.postgres
import llama_index.storage.index_store.postgres
import llama_index.vector_stores.milvus
import sqlalchemy
import sqlmodel

import log
import models
import services.corpus

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

    indices = {
        "keyword": {
            "doc_store": f"kw_doc_store_{corpus.id}",
            "idx_store": f"kw_idx_store_{corpus.id}",
        },
        "vector": corpus.name,
    }

    # download corpus source_uri to the local fs

    local_dir, local_files = services.corpus.download(source_uri=corpus.source_uri)
    files_count = len(local_files)
    files_md5 = services.corpus.files_fingerprint(files=local_files)

    logger.info(f"corpus {corpus.id} ingest '{corpus.name}' epoch {corpus.epoch} state '{corpus.state}'")

    if len(local_files) == 1 and local_files[0].endswith(".pdf"):
        docs = _load_pdf(file=local_files[0])
    elif len(local_files) == 1 and local_files[0] == "urls.txt":
        docs = _load_urls(local_dir=local_dir)
    else:
        docs = _load_dir(local_dir=local_dir)

    embed_model = services.corpus.embed_model(model=corpus.embed_model)

    if corpus.splitter == "semantic":
        text_splitter = llama_index.core.node_parser.SemanticSplitterNodeParser(
            buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
        )
    elif corpus.splitter.startswith("chunk"):
        chunk_size, chunk_overlap = _splitter_name_parse(name=corpus.splitter)
        text_splitter = llama_index.core.node_parser.SentenceSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap,
        )
    else:
        raise "invalid splitter"

    nodes = text_splitter.get_nodes_from_documents(docs)

    docs_count = len(docs)
    nodes_count = len(nodes)

    logger.info(f"corpus {corpus.id} ingest '{corpus.name}' epoch {corpus.epoch} state '{corpus.state}' docs {docs_count} nodes {nodes_count}")

    # vector index using milvus

    vector_store = llama_index.vector_stores.milvus.MilvusVectorStore(
        collection_name=corpus.name,
        dim=corpus.embed_dims,
        overwrite=True,
        uri=os.environ.get("MILVUS_URL"),
    )
    vector_storage_context = llama_index.core.StorageContext.from_defaults(
        vector_store=vector_store,
    )
    _vector_index = llama_index.core.VectorStoreIndex(
        nodes,
        embed_model=embed_model,
        show_progress=True,
        storage_context=vector_storage_context,
        store_nodes_override=True,
    )

    # keyword index using postgres

    # drop existing keyword indices
    _db_keyword_indices_drop(db_session=db_session, corpus=corpus)

    postgres_doc_store = llama_index.storage.docstore.postgres.PostgresDocumentStore.from_uri(
        perform_setup=True,
        table_name=indices.get("keyword").get("doc_store"),
        uri=os.environ.get("DATABASE_URL"),
    )
    postgres_index_store = llama_index.storage.index_store.postgres.PostgresIndexStore.from_uri(
        perform_setup=True,
        table_name=indices.get("keyword").get("idx_store"),
        uri=os.environ.get("DATABASE_URL"),
    )
    keyword_storage_context = llama_index.core.StorageContext.from_defaults(
        docstore=postgres_doc_store,
        index_store=postgres_index_store,
    )

    keyword_index = llama_index.core.SimpleKeywordTableIndex(
        nodes,
        embed_model=embed_model,
        # keyword_extract_template="KEYWORDS: sanjay,pegmo\n",
        max_keywords_per_chunk=KEYWORD_CHUNK_DEFAULT,
        storage_context=keyword_storage_context,
    )
    keyword_index.storage_context.persist()

    struct.seconds = (time.time() - t_start)

    corpus_meta = {
        "indices": indices,
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
    for table_name in corpus.keyword_tables:
        db_session.execute(sqlalchemy.text(f"drop table if exists {table_name}"))
    db_session.commit()


def _load_dir(local_dir: str) -> list:
    """
    Load docs within specified directory
    """
    reader = llama_index.core.SimpleDirectoryReader(local_dir)
    docs = reader.load_data()

    return docs


def _load_pdf(file: str) -> list:
    """
    Load pdf doc
    """
    reader = llama_index.readers.file.PDFReader()
    docs = reader.load_data(file)

    return docs


def _load_urls(local_dir: str) -> list:
    """
    Load urls
    """
    files = os.listdir(local_dir)

    if files[0] != "urls.txt":
        raise ValueError("expected urls.txt")

    path = f"{local_dir}/{files[0]}"
    urls = [url.strip() for url in open(path).read().split("\n") if url]

    docs = llama_index.readers.web.SimpleWebPageReader(html_to_text=True).load_data(urls)
    return docs


def _splitter_name_parse(name: str) -> tuple:
    _, chunk_size, chunk_overlap = name.split(":")

    return int(chunk_size), int(chunk_overlap)
