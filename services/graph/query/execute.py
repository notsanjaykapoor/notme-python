import neo4j


def execute(
    query: str,
    params: dict,
    session: neo4j.Session,
) -> list[neo4j.Record]:
    result = session.run(query, params)
    records = [record for record in result]
    summary = result.consume()  # noqa
    return records


def execute_with_summary(
    query: str,
    params: dict,
    session: neo4j.Session,
) -> tuple[list[neo4j.Record], neo4j.ResultSummary]:
    result = session.run(query, params)
    records = [record for record in result]
    summary = result.consume()
    return records, summary
