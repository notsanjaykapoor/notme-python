import neo4j


def read(tx: neo4j.Transaction, query: str, params: dict) -> neo4j.Result:
    return tx.run(query, params)


def write(tx: neo4j.Transaction, query: str, params: dict) -> neo4j.ResultSummary:
    result = tx.run(query, params)
    return result.consume()
