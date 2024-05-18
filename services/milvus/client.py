import os

import pymilvus


def client() -> list[str]:
    return pymilvus.MilvusClient(uri=os.environ.get("MILVUS_URL"))
