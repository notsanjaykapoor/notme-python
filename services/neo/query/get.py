import logging
import neo4j
import typing

import services.neo


def get(query: str, params: dict) -> typing.List[neo4j.Record]:
    driver = services.neo.get_driver()

    with driver.session() as session:
        result = session.run(query, params)
        records = [record for record in result]
        return records
