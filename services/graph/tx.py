import collections
import neo4j

GraphResult = collections.namedtuple("GraphResult", "records summary")


def read(tx: neo4j.Transaction, query: str, params: dict) -> list[neo4j.Record]:
    result = tx.run(query, params)
    records = [record for record in result]
    return records


def read_summary(tx: neo4j.Transaction, query: str, params: dict) -> GraphResult:
    result = tx.run(query, params)
    records = [record for record in result]
    summary = result.consume()
    return GraphResult(records=records, summary=summary)


def write(tx: neo4j.Transaction, query: str, params: dict) -> neo4j.ResultSummary:
    result = tx.run(query, params)
    return result.consume()
