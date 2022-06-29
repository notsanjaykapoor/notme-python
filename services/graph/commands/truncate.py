import neo4j


def truncate(session: neo4j.Session, batch_size: int = 100):
    query = f"match(n) call {{ with n detach delete n }} in transactions of {batch_size} rows"

    session.run(query)  # run with implicit transaction
