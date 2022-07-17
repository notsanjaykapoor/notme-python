import datadog

import env

from .types import GraphQuery


@datadog.statsd.timed("neo.reader", tags=[f"env:{env.name_random()}", f"reader:{__name__}"])
def match_shortest_path(src_label: str, src_id: str, dst_label: str, dst_id: str) -> GraphQuery:
    """find all shortest paths between nodes"""
    struct = GraphQuery("", {})

    struct.query = f"""
    match (p1:{src_label} {{id: $src_id}}), (p2:{dst_label} {{id: $dst_id}}), path = allShortestPaths((p1)-[r*]-(p2)) return path
    """

    struct.params = {
        "src_id": src_id,
        "dst_id": dst_id,
    }

    return struct
