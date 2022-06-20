import neo4j


def truncate(session: neo4j.Session):
    query = "MATCH(n) CALL { WITH n DETACH DELETE n } IN TRANSACTIONS OF 1000 ROWS"

    session.run(query)  # run with implicit transaction
