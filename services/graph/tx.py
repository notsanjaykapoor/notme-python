import neo4j


def read(tx: neo4j.Transaction, query: str, params: dict):
    return tx.run(query, params)


def write(tx: neo4j.Transaction, query: str, params: dict):
    return tx.run(query, params)
