import dataclasses
import typing


@dataclasses.dataclass
class GraphQuery:
    query: str
    params: dict


def match_node_count() -> GraphQuery:
    """return total node count"""
    struct = GraphQuery("", {})

    struct.query = "match (n) return count(n) as count"

    return struct


def match_node_label_count(label: str, id: typing.Optional[str]) -> GraphQuery:
    """return total node count filtered by label and optional id"""
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
    """return distinct labels grouped by count"""
    struct = GraphQuery("", {})

    struct.query = "match (n) return distinct labels(n) as label, count(*) as count"

    return struct


def match_relationship_count() -> GraphQuery:
    """return total relationship count"""
    struct = GraphQuery("", {})

    struct.query = "match(n)-[r]-(x) return count(r) as count"

    return struct
