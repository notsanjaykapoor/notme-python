import dataclasses
import os
import time

import llama_index.core
import llama_index.core.schema
import llama_index.core.vector_stores.utils
import more_itertools
import qdrant_client
import qdrant_client.models
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

    _local_dir, local_files = corpus.source_files
    files_count = len(local_files)
    files_md5 = services.corpus.fs.files_fingerprint(files=local_files)
    txt_docs, img_docs = services.corpus.load_docs(files=local_files)
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

    docs_count = len(txt_docs) + len(img_docs)
    nodes_count = len(txt_nodes)

    if txt_docs and img_docs:
        doc_type = "img_txt"
    elif img_docs:
        doc_type = "img" # deprecate
    else:
        doc_type = "txt"

    vector_store_name = os.environ.get("VECTOR_STORE")

    torch_device = services.corpus.torch_device()
    embed_model = services.corpus.models.resolve(model=model_name, device=torch_device)

    logger.info(
        f"corpus {corpus.id} ingest '{corpus.name}' model '{model_name}' epoch {corpus.epoch} store '{vector_store_name}' type '{doc_type}' docs {docs_count} nodes {nodes_count}"
    )

    if vector_store_name != "qdrant":
        raise ValueError("vector store invalid")

    client = services.qdrant.client()

    vector_img_name = ""
    vector_txt_name = ""

    logger.info(
        f"corpus {corpus.id} ingest '{corpus.name}' model '{model_name}' epoch {corpus.epoch} store '{vector_store_name}' text '{vector_txt_name}' image '{vector_img_name}'"
    )

    if txt_nodes:
        vector_txt_name = f"{corpus.name}_txt"

        # delete collection
        client.delete_collection(vector_txt_name)

        # generate text embeddings, create qdrant points, and upsert into qdrant collection

        chunked_i = 0

        for chunked_nodes in more_itertools.chunked(txt_nodes, 12):
            nodes_list = [node for node in chunked_nodes]
            txt_list = [node.get_content(metadata_mode=llama_index.core.schema.MetadataMode.EMBED) for node in chunked_nodes]

            txt_embeddings = embed_model.get_text_embedding_batch(
                txt_list,
                show_progress=True
            )

            txt_points: list[qdrant_client.models.PointStruct] = []

            for node, vector in zip(nodes_list, txt_embeddings):
                point = qdrant_client.models.PointStruct(
                    id=node.node_id,
                    payload=llama_index.core.vector_stores.utils.node_to_metadata_dict(node, remove_text=False, flat_metadata=False),
                    vector=vector,
                )

                txt_points.append(point)

            if chunked_i == 0:
                # create collection
                vector_size = len(txt_points[0].vector)

                client.create_collection(
                    collection_name=vector_txt_name,
                    vectors_config=qdrant_client.models.VectorParams(
                        size=vector_size,
                        distance=qdrant_client.models.Distance.COSINE,
                    ),
                )

            # update collection

            client.upsert(
                collection_name=vector_txt_name,
                points=txt_points,
            )

            chunked_i += 1

    if img_docs:
        vector_img_name = f"{corpus.name}_img"

        # delete collection
        client.delete_collection(vector_img_name)

        # generate image embeddings, create qdrant points, and upsert into qdrant collection

        chunked_i = 0

        for chunked_docs in more_itertools.chunked(img_docs, 12):
            docs_list = [doc for doc in chunked_docs]
            img_list = [doc.resolve_image() for doc in chunked_docs]

            img_embeddings = embed_model.get_image_embedding_batch(
                img_list,
                show_progress=True
            )

            img_points: list[qdrant_client.models.PointStruct] = []

            for node, vector in zip(docs_list, img_embeddings):
                point = qdrant_client.models.PointStruct(
                    id=node.node_id,
                    payload=llama_index.core.vector_stores.utils.node_to_metadata_dict(node, remove_text=False, flat_metadata=False),
                    vector=vector,
                )

                img_points.append(point)

            if chunked_i == 0:
                # create collection
                vector_size = len(img_points[0].vector)

                client.create_collection(
                    collection_name=vector_img_name,
                    vectors_config=qdrant_client.models.VectorParams(
                        size=vector_size,
                        distance=qdrant_client.models.Distance.COSINE,
                    ),
                )

            # update collection

            client.upsert(
                collection_name=vector_img_name,
                points=img_points,
            )

            chunked_i += 1

        # vector_storage_context = llama_index.core.StorageContext.from_defaults(
        #     vector_store=vector_txt_store,
        #     image_store=vector_img_store,
        # )

        # if vector_img_store and vector_txt_store:
        #     # use multi-modal index class
        #     _vector_index = llama_index.core.indices.MultiModalVectorStoreIndex(
        #         txt_nodes + img_docs,
        #         embed_model=embed_model,
        #         image_store=vector_img_store,
        #         show_progress=True,
        #         storage_context=vector_storage_context,
        #         vector_store=vector_txt_store,
        #     )
        # elif vector_txt_store:
        #     # use base vector store index class
        #     _vector_index = llama_index.core.VectorStoreIndex(
        #         txt_nodes,
        #         embed_model=embed_model,
        #         show_progress=True,
        #         storage_context=vector_storage_context,
        #         store_nodes_override=True,
        #         vector_store=vector_txt_store,
        #     )
        # elif vector_img_store:
        #     # VectorStoreIndex doesn't work with an image store only, so use MultiModalVectorStoreIndex
        #     _vector_index = llama_index.core.indices.MultiModalVectorStoreIndex(
        #         img_docs,
        #         embed_model=embed_model,
        #         image_store=vector_img_store,
        #         show_progress=True,
        #         storage_context=vector_storage_context,
        #         store_nodes_override=True,
        #         vector_store=vector_img_store, # normally, this would be a text store
        #     )

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
