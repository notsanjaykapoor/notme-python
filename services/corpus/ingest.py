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
import llama_index.vector_stores.milvus
import sqlmodel

import models
import services.corpus

@dataclasses.dataclass
class Struct:
    code: int
    docs_count: int
    nodes_count: int
    seconds: int
    errors: list[str]


CHUNK_SIZE_DEFAULT = 1024
CHUNK_OVERLAP_DEFAULT = 20


def ingest(db_session: sqlmodel.Session, name_encoded: str, dir: str, embed_model: llama_index.embeddings, embed_dims: int) -> Struct:
    """
    Load documents, split them into chunks, and generate and store embeddings in a local vector store.
    """
    struct = Struct(0, 0, 0, 0, [])

    t_start = time.time()

    files = os.listdir(dir)

    if files and files[0].endswith(".pdf"):
        docs = _load_pdf(file=f"{dir}/{files[0]}")
    elif files and files[0] == "urls.txt":
        docs = _load_urls(dir=dir)
    else:
        docs = _load_dir(dir=dir)

    # splitter = llama_index.core.node_parser.SentenceSplitter(chunk_size=CHUNK_SIZE_DEFAULT, chunk_overlap=CHUNK_OVERLAP_DEFAULT)
    splitter = llama_index.core.node_parser.SemanticSplitterNodeParser(
        buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
    )
    nodes = splitter.get_nodes_from_documents(docs)

    vector_store = llama_index.vector_stores.milvus.MilvusVectorStore(
        collection_name=name_encoded,
        dim=embed_dims,
        overwrite=True,
        uri=os.environ.get("MILVUS_URL"),
    )
    storage_context = llama_index.core.StorageContext.from_defaults(
        vector_store=vector_store,
    )
    _vector_index = llama_index.core.VectorStoreIndex(
        nodes,
        embed_model=embed_model,
        show_progress=True,
        storage_context=storage_context,
        store_nodes_override=True,
    )

    struct.docs_count = len(docs)
    struct.nodes_count = len(nodes)
    struct.seconds = (time.time() - t_start)

    parse_result = services.corpus.name_parse(name_encoded=name_encoded)
    embed_model = parse_result.model

    _db_write(
        db_session=db_session,
        collection_name=name_encoded,
        embed_model=embed_model,
        embed_dims=embed_dims,
        corpus_params={
            "docs_count": struct.docs_count,
            "nodes_count": struct.nodes_count,
            "state": models.corpus.STATE_INGESTED,
        }
    )

    return struct


def _db_write(db_session: sqlmodel.Session, collection_name: str, embed_model: str, embed_dims: int, corpus_params: dict) -> int:
    """
    Create or update database corpus object
    """
    code = 0

    db_select = sqlmodel.select(models.Corpus).where(models.Corpus.collection_name == collection_name)
    db_object = db_session.exec(db_select).first()

    if db_object:
        db_object.docs_count = corpus_params.get("docs_count")
        db_object.nodes_count = corpus_params.get("nodes_count")
        db_object.state = corpus_params.get("state")
        db_object.updated_at = datetime.datetime.now(datetime.timezone.utc)

        code = 200
    else:
        db_object = models.Corpus(
            collection_name=collection_name,
            docs_count=corpus_params.get("docs_count"),
            embed_dims=embed_dims,
            embed_model=embed_model,
            nodes_count=corpus_params.get("nodes_count"),
            org_id=0,
            state=corpus_params.get("state"),
        )

        code = 201

    db_session.add(db_object)
    db_session.commit()

    return code


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
    urls = [url.strip() for url in open(path).read().split("\n")]

    docs = llama_index.readers.web.SimpleWebPageReader(html_to_text=True).load_data(urls)
    return docs
