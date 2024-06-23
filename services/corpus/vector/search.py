import dataclasses
import os
import time

import llama_index.core
import llama_index.core.schema
import llama_index.core.settings
import llama_index.core.vector_stores.utils
import qdrant_client
import qdrant_client.http.models.models
import qdrant_client.models

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

    qdrant_points = _qdrant_query(corpus=corpus, query=query, similarity_top_k=limit)
    struct.nodes = _qdrant_points_to_nodes(points=qdrant_points)

    struct.msec = (time.time() - t_start) * 1000

    return struct


def _qdrant_points_to_nodes(points: list[qdrant_client.http.models.ScoredPoint]) -> list[llama_index.core.schema.NodeWithScore]:
    """
    Map qdrant points to node objects
    """
    node_with_scores = []

    for point in points:
        node = llama_index.core.vector_stores.utils.metadata_dict_to_node(point.payload)
        node_with_scores.append(llama_index.core.schema.NodeWithScore(node=node, score=point.score))

    return node_with_scores


def _qdrant_query(corpus: models.Corpus, query: str, similarity_top_k: int) -> list[qdrant_client.http.models.ScoredPoint]:
    """
    run vector search and return points results
    """
    # map query to vector
    torch_device = services.corpus.torch_device()
    embed_model = services.corpus.models.resolve(model=corpus.model_name, device=torch_device)
    query_vector = embed_model.get_agg_embedding_from_queries([query])

    vector_store_name = os.environ.get("VECTOR_STORE")

    if vector_store_name != "qdrant":
        raise ValueError("vector store invalid")

    client = qdrant_client.QdrantClient(url=os.environ.get("QDRANT_URL"))

    logger.info(
        f"{context.rid_get()} corpus '{corpus.name}' model '{corpus.model_name}' load - text '{corpus.vector_txt_uri}' image '{corpus.vector_img_uri}'"
    )

    if not corpus.vector_txt_uri and not corpus.vector_img_uri:
        raise ValueError("corpus'{corpus.name}' missing image or text store")

    if corpus.vector_txt_uri:
        vector_txt_name = corpus.vector_txt_uri.split(":")[-1]

        qdrant_response = client.search(
            collection_name=vector_txt_name,
            query_vector=query_vector,
            limit=similarity_top_k,
            query_filter=qdrant_client.models.Filter(),
        )

        return qdrant_response

    if corpus.vector_img_uri:
        vector_img_name = corpus.vector_img_uri.split(":")[-1]

        qdrant_response = client.search(
            collection_name=vector_img_name,
            query_vector=query_vector,
            limit=similarity_top_k,
            query_filter=qdrant_client.models.Filter(),
        )

        return qdrant_response
    
