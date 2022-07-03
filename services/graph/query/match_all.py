import dataclasses


@dataclasses.dataclass
class GraphQuery:
    query: str
    params: dict


def match_all() -> GraphQuery:
    """query for all nodes"""
    struct = GraphQuery("", {})

    struct.query = "match (n) return n"

    return struct
