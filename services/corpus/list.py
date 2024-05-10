import dataclasses

import sqlalchemy
import sqlmodel

@dataclasses.dataclass
class Struct:
    code: int
    errors: list[str]
    names: list[str]


def list_all(db_url: str) -> Struct:
    """
    List all corpus database names by querying postgres databases
    """
    struct = Struct(0, [], [])

    engine = sqlmodel.create_engine(db_url, echo=False)

    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
        struct.names = sorted([row[0] for row in result if row[0].startswith("c:")])

    return struct


