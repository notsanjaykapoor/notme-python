import services.milvus


def delete_by_name(collection: str) -> int:
    """
    Delete milvus collection
    """
    collections = services.milvus.list()

    if collection not in collections:
        return 404

    client = services.milvus.client()
    client.drop_collection(collection)

    return 0
