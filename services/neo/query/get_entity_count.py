import logging
import neo4j
import os
import sys

import services.neo


def get_entity_count() -> int:
    driver = services.neo.get_driver()

    query = "MATCH(n) return count(*) as count"

    with driver.session() as session:
        result = session.run(query)  # run with explicit transaction
        record = result.single()
        return record["count"]
