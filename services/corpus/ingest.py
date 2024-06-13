import dataclasses
import os
import time

import llama_index.core
import llama_index.core.indices
import llama_index.core.node_parser
import llama_index.storage.docstore.postgres
import llama_index.vector_stores.qdrant
import sqlalchemy
import sqlmodel

import log
import models
import services.corpus
import services.corpus.fs
import services.corpus.models
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

    storage = {}

    local_dir, local_files = corpus.source_files
    files_count = len(local_files)
    files_md5 = services.corpus.fs.files_fingerprint(files=local_files)
    docs_txt, docs_img = services.corpus.load_docs(files=local_files)
    model_name = corpus.model_name
    splitter = models.corpus.SPLITTER_NAME_DEFAULT

    if model_name.startswith("auto"):
        # auto detect model
        model_name = services.corpus.models.detect(files=local_files)

    logger.info(f"corpus {corpus.id} ingest '{corpus.name}' model '{model_name}' epoch {corpus.epoch} state '{corpus.state}'")

    if docs_txt:
        # split text docs
        nodes_txt = services.corpus.split_docs(docs=docs_txt, splitter=splitter)
    else:
        nodes_txt = []

    docs_count = len(docs_txt) + len(docs_img)
    nodes_count = len(nodes_txt)

    vector_store_name = os.environ.get("VECTOR_STORE")

    torch_device = services.corpus.torch_device()
    model_klass = services.corpus.models.resolve(model=model_name, device=torch_device)

    logger.info(
        f"corpus {corpus.id} ingest '{corpus.name}' model '{model_name}' epoch {corpus.epoch} store '{vector_store_name}' docs {docs_count} nodes {nodes_count}"
    )

    if vector_store_name == "faiss":
        # vector index using faiss
        vector_store = llama_index.vector_stores.faiss.FaissVectorStore(faiss_index=faiss.IndexFlatL2(corpus.model_dims))

        vector_storage_context = llama_index.core.StorageContext.from_defaults(
            vector_store=vector_store,
        )

        vector_index = llama_index.core.VectorStoreIndex(
            nodes_txt,
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
    elif vector_store_name == "postgres":
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
            nodes_txt,
            embed_model=model_klass,
            show_progress=True,
            storage_context=vector_storage_context,
            store_nodes_override=True,
        )
    elif vector_store_name == "qdrant":
        client = services.qdrant.client()

        vector_img_name = ""
        vector_img_store = None
        vector_txt_name = ""
        vector_txt_store = None

        if nodes_txt:
            # create text store
            vector_txt_name = f"{corpus.name}_txt"

            client.delete_collection(vector_txt_name)

            vector_txt_store = llama_index.vector_stores.qdrant.QdrantVectorStore(
                client=client,
                collection_name=vector_txt_name,
            )

        if docs_img:
            vector_img_name = f"{corpus.name}_img"

            # create image store
            client.delete_collection(vector_img_name)

            vector_img_store = llama_index.vector_stores.qdrant.QdrantVectorStore(
                client=client,
                collection_name=vector_img_name,
            )

        vector_storage_context = llama_index.core.StorageContext.from_defaults(
            vector_store=vector_txt_store,
            image_store=vector_img_store,
        )

        logger.info(
            f"corpus {corpus.id} ingest '{corpus.name}' model '{model_name}' epoch {corpus.epoch} store '{vector_store_name}' text '{vector_txt_name}' image '{vector_img_name}'"
        )

        if vector_img_store and vector_txt_store:
            # use multi-modal index class
            _vector_index = llama_index.core.indices.MultiModalVectorStoreIndex(
                nodes_txt + docs_img,
                embed_model=model_klass,
                image_store=vector_img_store,
                show_progress=True,
                storage_context=vector_storage_context,
                vector_store=vector_txt_store,
            )
        elif vector_txt_store:
            # use base vector store index class
            _vector_index = llama_index.core.VectorStoreIndex(
                nodes_txt,
                embed_model=model_klass,
                show_progress=True,
                storage_context=vector_storage_context,
                store_nodes_override=True,
                vector_store=vector_txt_store,
            )
        elif vector_img_store:
            # VectorStoreIndex doesn't work with an image store only, so use MultiModalVectorStoreIndex
            _vector_index = llama_index.core.indices.MultiModalVectorStoreIndex(
                docs_img,
                embed_model=model_klass,
                image_store=vector_img_store,
                show_progress=True,
                storage_context=vector_storage_context,
                store_nodes_override=True,
                vector_store=vector_img_store, # normally, this would be a text store
            )

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
            nodes_txt,
            embed_model=model_klass,
            # keyword_extract_template="KEYWORDS: sanjay,pegmo\n",
            max_keywords_per_chunk=KEYWORD_CHUNK_DEFAULT,
            storage_context=keyword_storage_context,
        )
        keyword_index.storage_context.persist()

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

    if vector_img_name:
        corpus.vector_img_uri = f"qdrant:{vector_img_name}"

    if vector_txt_name:
        corpus.vector_txt_uri = f"qdrant:{vector_txt_name}"

    db_session.add(corpus)
    db_session.commit()

    struct.corpus = corpus

    logger.info(f"corpus {corpus.id} ingest '{corpus.name}' model '{corpus.model_name}' epoch {corpus.epoch} state '{corpus.state}'")

    return struct


def _db_keyword_indices_drop(db_session: sqlmodel.Session, corpus: models.Corpus) -> int:
    """
    """
    for table_name in corpus.storage_keyword_tables:
        db_session.execute(sqlalchemy.text(f"drop table if exists {table_name}"))
    db_session.commit()

