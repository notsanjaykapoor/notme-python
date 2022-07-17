import datadog

import env

from .types import GraphQuery


@datadog.statsd.timed("neo.reader", tags=[f"env:{env.name_random()}", f"reader:{__name__}"])
def match_neighbors(src_label: str, src_id: str, max_hops: int, dst_label: str = None) -> GraphQuery:
    """find all node neighbors filtered by dst label and constrained by hops"""
    struct = GraphQuery("", {})

    if dst_label:
        struct.query = f"match path = (a:{src_label} {{id: $src_id}})-[*1.." + str(max_hops) + "]-(b) " f"where (b:{dst_label}) " + "return path"
    else:
        struct.query = f"match path = (a:{src_label} {{id: $src_id}})-[*1.." + str(max_hops) + "]-(b) return path"

    struct.params = {"src_id": src_id}

    return struct
