import dataclasses


@dataclasses.dataclass
class GraphQuery:
    query: str
    params: dict


def match_neighbors(node_label: str, node_id: str, max_hops: int, dst_labels: list[list[str]]) -> GraphQuery:
    """find all node neighbors filtered by dst label and constrained by hops"""

    struct = GraphQuery("", {})

    struct.query = (
        f"match p = (a:{node_label} {{id: $node_id}})-[*1.." + str(max_hops) + "]-(b) "
        f"where labels(b) in {dst_labels} " + "return distinct(b) as n"
    )

    struct.params = {"node_id": node_id}

    return struct
