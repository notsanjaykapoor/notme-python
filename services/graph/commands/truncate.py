import services.graph.driver


def truncate():
    driver = services.graph.driver.get()

    query = "MATCH(n) CALL { WITH n DETACH DELETE n } IN TRANSACTIONS OF 1000 ROWS"

    with driver.session() as session:
        session.run(query)  # run with implicit transaction
