import datadog

from .types import GraphQuery


@datadog.statsd.timed("neo.reader", tags=[f"reader:{__name__}"])
def match_random(limit: int) -> GraphQuery:
    """query random node set"""
    struct = GraphQuery("", {})

    struct.query = f"match(n) with n as node, rand() as r return node order by r limit {limit}"

    return struct
