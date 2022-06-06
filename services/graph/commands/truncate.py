import logging
import neo4j
import os
import sys

import services.graph


def truncate():
    driver = services.graph.get_driver()

    query = "MATCH(n) CALL { WITH n DETACH DELETE n } IN TRANSACTIONS OF 1000 ROWS"

    with driver.session() as session:
        session.run(query)  # run with implicit transaction
