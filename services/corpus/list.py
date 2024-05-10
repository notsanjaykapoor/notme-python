import dataclasses

import sqlalchemy
import sqlmodel

import services.corpus

@dataclasses.dataclass
class Struct:
    code: int
    databases: list[dict]
    errors: list[str]


def list_all(db_url: str) -> Struct:
    """
    List all corpus database names by querying postgres databases
    """
    struct = Struct(0, [], [])

    engine = sqlmodel.create_engine(db_url, echo=False)

    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
        names = sorted([row[0] for row in result])

    for name in names:
        parse_result = services.corpus.name_parse(database=name)

        if parse_result.code != 0:
            continue

        corpus = parse_result.corpus
        model = parse_result.model
        name = f"corpus '{corpus}' model '{model}'"
        struct.databases.append({
            "corpus": corpus,
            "database": parse_result.database,
            "model": model,
            "name": name,
        })

    return struct


