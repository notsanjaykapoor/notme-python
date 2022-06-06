import logging
import neo4j
import typing

import services.neo


def execute(
    query: str,
    params: dict,
    driver: typing.Optional[neo4j.Driver] = None,
) -> typing.List[neo4j.Record]:
    if not driver:
        driver = services.neo.get_driver()

    with driver.session() as session:
        result = session.run(query, params)
        records = [record for record in result]
        return records
