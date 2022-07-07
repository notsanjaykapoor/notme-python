import dataclasses
import re


@dataclasses.dataclass
class GraphQuery:
    query: str
    params: dict


def match_node(id: str) -> GraphQuery:
    """query to match specified node"""
    struct = GraphQuery("", {})

    if re.match(r"^[A-Z0-9]{26}$", id):
        # match node id
        struct.query = "match(node {id: $id}) return node"
    else:
        # match node name
        struct.query = "match (node {name: $id}) return node"

    struct.params = {"id": id}

    return struct
