import os

import pymilvus

import services.milvus


def delete_by_name(collection: str) -> int:
    collections = services.milvus.list_()

    if collection not in collections:
        return 404

    client = pymilvus.MilvusClient(uri=os.environ.get("MILVUS_URL"))
    client.drop_collection(collection)

    return 0
