import os

import neo4j


def get() -> neo4j.Session:
    session = _get_driver().session(database=os.environ["NEO4J_DB_NAME"])

    return session


def _get_driver() -> neo4j.Driver:
    driver = neo4j.GraphDatabase.driver(
        os.environ["NEO4J_BOLT_URL"],
        auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]),
    )

    return driver
