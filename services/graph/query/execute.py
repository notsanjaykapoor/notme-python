import neo4j
import typing

import services.graph
import services.graph.driver


def execute(
    query: str,
    params: dict,
    driver: typing.Optional[neo4j.Driver] = None,
) -> list[neo4j.Record]:
    if not driver:
        driver = services.graph.driver.get()

    with driver.session() as session:
        result = session.run(query, params)
        records = [record for record in result]
        summary = result.consume()
        return records


def execute_with_summary(
    query: str,
    params: dict,
    driver: typing.Optional[neo4j.Driver] = None,
) -> tuple[list[neo4j.Record], neo4j.ResultSummary]:
    if not driver:
        driver = services.graph.driver.get()

    with driver.session() as session:
        result = session.run(query, params)
        records = [record for record in result]
        summary = result.consume()
        return records, summary
