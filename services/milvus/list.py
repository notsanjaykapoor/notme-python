import services.milvus


def list_details() -> list[dict]:
    client = services.milvus.client()
    return [client.describe_collection(collection) for collection in list()]


def list() -> list[str]:
    client = services.milvus.client()
    return sorted(client.list_collections())
