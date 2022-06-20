import os

import neo4j

import services.graph.driver


def get() -> neo4j.Session:
    session = services.graph.driver.get().session(database=os.environ["NEO4J_DB_NAME"])

    return session
