import os

import pymilvus


def list_() -> list[str]:
    client = pymilvus.MilvusClient(uri=os.environ.get("MILVUS_URL"))
    return sorted(client.list_collections())


def list_details() -> list[dict]:
    client = pymilvus.MilvusClient(uri=os.environ.get("MILVUS_URL"))
    return [client.describe_collection(collection) for collection in list_()]