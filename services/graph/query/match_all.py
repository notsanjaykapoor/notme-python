import dataclasses


@dataclasses.dataclass
class GraphQuery:
    query: str
    params: dict


def match_all(format: str) -> GraphQuery:
    """query for all nodes"""
    struct = GraphQuery("", {})

    if format == "wide":
        # struct.query = "match(node)-[edge]-(dst) return node, edge, dst, id(node) as src_gid, id(dst) as dst_gid"
        struct.query = "match(node)-[edge]-(dst) return node, edge"
    else:
        struct.query = "match (node) return node"

    return struct
