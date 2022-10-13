import datadog

from .types import GraphQuery


@datadog.statsd.timed("neo.reader", tags=[f"reader:{__name__}"])
def match_edges(src_label: str, src_id: str) -> GraphQuery:
    struct = GraphQuery("", {})

    struct.query = f"match p = (a:{src_label} {{id: $src_id}})-[e]-(x) return e"
    struct.params = {"src_id": src_id}

    return struct
