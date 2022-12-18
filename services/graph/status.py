import neo4j

import services.graph.query


def status_up(neo: neo4j.Session) -> int:
    """check graph server is up"""

    try:
        query = "match() return 1 limit 1"
        result = services.graph.query.execute(query, {}, neo)
        return 0
    except Exception:
        return -1
