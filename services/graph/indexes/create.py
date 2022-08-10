import neo4j

import services.graph.query


def create(session: neo4j.Session) -> int:
    added = 0

    added += create_entity_unique_idx(session)
    added += create_link_idx(session)
    added += create_property_idx(session)

    return added


def create_entity_unique_idx(session: neo4j.Session) -> int:
    """create neo4j unique constraint on entity.id, which also adds an index"""
    records, summary = services.graph.query.execute_with_summary(
        query="create constraint entity_id_unique_idx if not exists for (n:entity) require n.id is unique",
        params={},
        session=session,
    )

    return summary.counters.constraints_added


def create_link_idx(session: neo4j.Session) -> int:
    """create neo4j index on link.id"""
    records, summary = services.graph.query.execute_with_summary(
        query="create index link_id_idx if not exists for (n:link) on (n.id)",
        params={},
        session=session,
    )

    return summary.counters.indexes_added


def create_property_idx(session: neo4j.Session) -> int:
    """create neo4j index on property.id"""
    records, summary = services.graph.query.execute_with_summary(
        query="create index prop_id_idx if not exists for (n:property) on (n.id)",
        params={},
        session=session,
    )

    return summary.counters.indexes_added
