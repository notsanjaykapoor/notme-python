import dataclasses


@dataclasses.dataclass
class GraphQuery:
    query: str
    params: dict


def match_all() -> GraphQuery:
    """query for all nodes"""
    struct = GraphQuery("", {})

    struct.query = "match (node) return node"

    return struct


def match_all_no_edges() -> GraphQuery:
    """query for all nodes without edges"""
    struct = GraphQuery("", {})

    struct.query = "match(node) where not (node)--() return node"

    return struct


def match_all_with_edges() -> GraphQuery:
    """query for all nodes with edges"""
    struct = GraphQuery("", {})

    struct.query = "match(node)-[edge]-() return node, edge"

    return struct
