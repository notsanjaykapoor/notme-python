import logging
import neo4j
import os
import sys


def get_driver() -> neo4j.Driver:
    driver = neo4j.GraphDatabase.driver(
        os.environ["NEO4J_BOLT_URL"],
        auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]),
    )

    return driver
