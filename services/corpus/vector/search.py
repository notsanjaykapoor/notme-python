import dataclasses
import os
import time

import qdrant_client
import qdrant_client.http.models
import qdrant_client.models

import embetter.multi

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



logger = log.init("api")



def search(corpus: models.Corpus, query: str, limit: int) -> StructNodes:
    """
    """
    struct = StructNodes(
        code=0,
        msec=0, 
        nodes=[],
        errors=[],
    )

    t_start = time.time()

    qdrant_points = _qdrant_query_text(corpus=corpus, query=query, similarity_top_k=limit)
    struct.nodes = _qdrant_points_to_nodes(points=qdrant_points)

    struct.msec = (time.time() - t_start) * 1000

    return struct


def _qdrant_points_to_nodes(points: list[qdrant_client.http.models.ScoredPoint]) -> list[models.NodeImage | models.NodeText]:
    """
    Map qdrant points to node objects
    """
    nodes = []

    for point in points:
        if point.payload.get("node_type") == "txt":
            node = models.NodeText(
                id=point.id,
                file_name=point.payload.get("file_name"),
                page_label=point.payload.get("page_label"),
                score=point.score,
                text=point.payload.get("text"),
            )
        else:
            node = models.NodeImage(
                caption=point.payload.get("caption"),
                id=point.id,
                name=point.payload.get("name"),
                score=point.score,
                uri=point.payload.get("uri"),
            )
            # node = llama_index.core.vector_stores.utils.metadata_dict_to_node(point.payload)

        nodes.append(node)

    return nodes


def _qdrant_query_text(corpus: models.Corpus, query: str, similarity_top_k: int) -> list[qdrant_client.http.models.ScoredPoint]:
    """
    run vector search and return points results
    """
    # map query to vector
    torch_device = services.corpus.torch_device()
    embed_model = services.corpus.models.resolve(model=corpus.model_name, device=torch_device)
    # query_vector = embed_model.get_agg_embedding_from_queries([query])
    query_vector = embed_model.get_text_embedding(query)
    # query_vector = embetter.multi.ClipEncoder().transform(query)

    vector_store_name = os.environ.get("VECTOR_STORE")

    if vector_store_name != "qdrant":
        raise ValueError("vector store invalid")

    client = qdrant_client.QdrantClient(url=os.environ.get("QDRANT_URL"))

    logger.info(
        f"{context.rid_get()} corpus '{corpus.name}' model '{corpus.model_name}' load '{corpus.source_type}'"
    )

    if not corpus.vector_txt_uri and not corpus.vector_img_uri:
        raise ValueError("corpus'{corpus.name}' missing image or text store")

    if corpus.vector_txt_uri:
        collection_name = corpus.vector_txt_uri.split(":")[-1]
    elif corpus.vector_img_uri:
        collection_name = corpus.vector_img_uri.split(":")[-1]

    qdrant_response = client.search(
        collection_name=collection_name,
        query_vector=qdrant_client.http.models.NamedVector(
            name="txt",
            vector=query_vector,
        ),
        limit=similarity_top_k,
        query_filter=qdrant_client.models.Filter(),
    )

    return qdrant_response
    
