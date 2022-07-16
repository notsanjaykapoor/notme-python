import typing

from .types import GraphQuery


def match_edges_count(names: typing.Optional[str] = None) -> GraphQuery:
    """query total edges count"""
    struct = GraphQuery("", {})

    if names:
        struct.query = f"match(n)-[r:{names}]-(x) return count(r) as count"
    else:
        struct.query = "match(n)-[r]-(x) return count(r) as count"

    return struct


def match_node_count() -> GraphQuery:
    """query total node count"""
    struct = GraphQuery("", {})

    struct.query = "match (n) return count(n) as count"

    return struct


def match_node_label_count(label: str, id: typing.Optional[str]) -> GraphQuery:
    """query total node count filtered by label and optional id"""
    struct = GraphQuery("", {})

    if id:
        struct.query = f"match (n:{label} {{id: $id}}) return count(n) as count"
    else:
        struct.query = f"match (n:{label}) return count(n) as count"

    struct.params = {
        "id": id,
    }

    return struct


def match_node_label_group_count() -> GraphQuery:
    """query distinct labels grouped by count"""
    struct = GraphQuery("", {})

    struct.query = "match (n) return distinct labels(n) as label, count(*) as count"

    return struct
