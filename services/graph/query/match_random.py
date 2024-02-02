from .types import GraphQuery


def match_random(limit: int) -> GraphQuery:
    """query random node set"""
    struct = GraphQuery("", {})

    struct.query = f"match(n) with n as node, rand() as r return node order by r limit {limit}"

    return struct
