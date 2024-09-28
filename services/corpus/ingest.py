import dataclasses
import os
import time

import sqlmodel

import log
import models
import services.corpus
import services.corpus.fs
import services.corpus.models
import services.images
import services.qdrant

@dataclasses.dataclass
class Struct:
    code: int
    corpus: models.Corpus
    seconds: int
    errors: list[str]


DOC_CHUNK_SIZE_DEFAULT = 512

KEYWORD_CHUNK_DEFAULT = 1024

VECTOR_CHUNK_SIZE_DEFAULT = 1024
VECTOR_CHUNK_OVERLAP_DEFAULT = 20

logger = log.init("app")

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

    t_start = time.time()

    # initialize corpus state

    corpus.state = models.corpus.STATE_PROCESSING
    db_session.add(corpus)
    db_session.commit()

    _local_dir, local_files = corpus.source_files
    files_count = len(local_files)
    files_md5 = services.corpus.fs.files_fingerprint(files=local_files)
    txt_docs, img_nodes = services.corpus.load_docs(files=local_files)
    model_name = corpus.model_name
    splitter = models.corpus.SPLITTER_NAME_DEFAULT

    if model_name.startswith("auto"):
        # auto detect model
        model_name = services.corpus.models.detect(files=local_files)

    logger.info(f"corpus {corpus.id} ingest '{corpus.name}' model '{model_name}' epoch {corpus.epoch} state '{corpus.state}'")

    if txt_docs:
        # split text docs into nodes
        txt_nodes = services.corpus.split_docs(docs=txt_docs, splitter=splitter)
    else:
        txt_nodes = []

    docs_count = len(txt_docs) + len(img_nodes)
    nodes_count = len(txt_nodes) + len(img_nodes)

    vector_store_name = os.environ.get("VECTOR_STORE")

    torch_device = services.corpus.torch_device()
    embed_model = services.corpus.models.resolve(model=model_name, device=torch_device)

    logger.info(
        f"corpus {corpus.id} ingest '{corpus.name}' model '{model_name}' epoch {corpus.epoch} store '{vector_store_name}' files {files_count} docs {docs_count} nodes {nodes_count}"
    )

    if vector_store_name != "qdrant":
        raise ValueError("vector store invalid")

    if not txt_nodes and not img_nodes:
        raise ValueError("text or images must be specified")

    if txt_nodes and img_nodes:
        raise ValueError("text and images not supported")

    if txt_nodes:
        vector_name = services.corpus.ingest_qdrant_text(corpus=corpus, nodes=txt_nodes, embed_model=embed_model)
        corpus.vector_txt_uri = f"qdrant:{vector_name}"

    if img_nodes:
        vector_name = services.corpus.ingest_qdrant_multi(corpus=corpus, nodes=img_nodes, embed_model=embed_model)
        corpus.vector_img_uri = f"qdrant:{vector_name}"

    struct.seconds = (time.time() - t_start)

    corpus_meta = {
        "device": torch_device,
    }

    # update corpus

    corpus.docs_count = docs_count
    corpus.files_count = files_count
    corpus.meta = corpus.meta | corpus_meta
    corpus.model_name = model_name
    corpus.nodes_count = nodes_count
    corpus.fingerprint = files_md5
    corpus.splitter = splitter
    corpus.state = models.corpus.STATE_INGESTED

    db_session.add(corpus)
    db_session.commit()

    struct.corpus = corpus

    logger.info(f"corpus {corpus.id} ingest '{corpus.name}' model '{corpus.model_name}' epoch {corpus.epoch} state '{corpus.state}' type '{corpus.source_type}'")

    return struct
