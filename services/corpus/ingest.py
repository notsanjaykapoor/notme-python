import dataclasses
import datetime
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

import models
import services.corpus

@dataclasses.dataclass
class Struct:
    code: int
    docs_count: int
    epoch: int
    nodes_count: int
    seconds: int
    errors: list[str]


KEYWORD_CHUNK_DEFAULT = 1024

VECTOR_CHUNK_SIZE_DEFAULT = 1024
VECTOR_CHUNK_OVERLAP_DEFAULT = 20


def ingest(
    db_session: sqlmodel.Session,
    name_encoded: str,
    dir: str,
    embed_model: llama_index.embeddings,
    embed_dims: int,
    splitter: str,
    epoch: int=0,
) -> Struct:
    """
    Load documents, split them into chunks, and generate and store embeddings in a local vector store.
    """
    struct = Struct(0, 0, 0, 0, 0, [])

    t_start = time.time()

    if not epoch:
        epoch = services.corpus.epoch_generate(db_session=db_session, name_encoded=name_encoded)

    model_name = embed_model.model_name.split("/")[-1]

    # initialize corpus state

    db_object, db_code = _db_write(
        db_session=db_session,
        name=name_encoded,
        embed_model=model_name,
        embed_dims=embed_dims,
        epoch=epoch,
        params={
            "source_dir": dir,
        },
        state=models.corpus.STATE_PENDING,
    )

    indices = {
        "keyword": {
            "doc_store": f"kw_doc_store_{db_object.id}",
            "idx_store": f"kw_idx_store_{db_object.id}",
        },
        "vector": name_encoded,
    }

    files = os.listdir(dir)

    if len(files) == 1 and files[0].endswith(".pdf"):
        docs = _load_pdf(file=f"{dir}/{files[0]}")
    elif len(files) == 1 and files[0] == "urls.txt":
        docs = _load_urls(dir=dir)
    else:
        docs = _load_dir(dir=dir)

    if splitter == "semantic":
        text_splitter = llama_index.core.node_parser.SemanticSplitterNodeParser(
            buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
        )
    elif splitter.startswith("chunk"):
        chunk_size, chunk_overlap = _chunk_parse(name=splitter)
        text_splitter = llama_index.core.node_parser.SentenceSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap,
        )
    else:
        raise "invalid splitter"

    nodes = text_splitter.get_nodes_from_documents(docs)

    # vector index using milvus

    vector_store = llama_index.vector_stores.milvus.MilvusVectorStore(
        collection_name=name_encoded,
        dim=embed_dims,
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

    if db_code == 200:
        # truncate existing indices
        _db_index_truncate(db_session=db_session, corpus=db_object)

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

    struct.docs_count = len(docs)
    struct.epoch = epoch
    struct.nodes_count = len(nodes)
    struct.seconds = (time.time() - t_start)

    corpus_meta = {
        "indices": indices,
        "splitter": splitter,
    }

    # update corpus state

    _db_write(
        db_session=db_session,
        name=name_encoded,
        embed_model=model_name,
        embed_dims=embed_dims,
        epoch=epoch,
        params={
            "docs_count": struct.docs_count,
            "meta": corpus_meta,
            "nodes_count": struct.nodes_count,
            "source_dir": dir,
        },
        state=models.corpus.STATE_INGESTED,
    )

    return struct


def _db_index_truncate(db_session: sqlmodel.Session, corpus: models.Corpus) -> int:
    """
    """
    for table_name in corpus.keyword_tables:
        db_session.execute(sqlalchemy.text(f"delete from {table_name}"))
    db_session.commit()


def _db_write(db_session: sqlmodel.Session, name: str, embed_model: str, embed_dims: int, epoch: int, state: str, params: dict) -> tuple:
    """
    Create or update database corpus object
    """
    code = 0

    db_object = services.corpus.get_by_name(db_session=db_session, name=name)

    if db_object:
        code = 200
    else:
        db_object = models.Corpus()
        code = 201

    db_object.docs_count = params.get("docs_count") or 0
    db_object.embed_dims=embed_dims
    db_object.embed_model=embed_model
    db_object.epoch = epoch
    if meta := params.get("meta"):
        db_object.meta = meta
    db_object.name = name
    db_object.nodes_count = params.get("nodes_count") or 0
    db_object.org_id = 0
    db_object.source_dir = params.get("source_dir")
    db_object.state = state
    db_object.updated_at = datetime.datetime.now(datetime.timezone.utc)

    db_session.add(db_object)
    db_session.commit()

    return db_object, code


def _chunk_parse(name: str) -> tuple:
    _, chunk_size, chunk_overlap = name.split(":")

    return int(chunk_size), int(chunk_overlap)


def _load_dir(dir: str) -> list:
    """
    Load docs within specified directory
    """
    reader = llama_index.core.SimpleDirectoryReader(dir)
    docs = reader.load_data()

    return docs


def _load_pdf(file: str) -> list:
    """
    Load pdf doc
    """
    reader = llama_index.readers.file.PDFReader()
    docs = reader.load_data(file)

    return docs


def _load_urls(dir: str) -> list:
    """
    Load urls
    """
    files = os.listdir(dir)

    if files[0] != "urls.txt":
        raise ValueError("expected urls.txt")

    path = f"{dir}/{files[0]}"
    urls = [url.strip() for url in open(path).read().split("\n") if url]

    docs = llama_index.readers.web.SimpleWebPageReader(html_to_text=True).load_data(urls)
    return docs
