import os

import qdrant_client


def client():
    return qdrant_client.QdrantClient(url=os.environ.get("QDRANT_URL"))