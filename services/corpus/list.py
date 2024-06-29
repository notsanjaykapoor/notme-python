import dataclasses
import re

import sqlalchemy
import sqlmodel

import models
import services.corpus
import services.mql

@dataclasses.dataclass
class Struct:
    code: int
    objects: list[models.User]
    count: int
    total: int
    errors: list[str]


def list(db_session: sqlmodel.Session, query: str = "", offset: int = 0, limit: int = 20) -> Struct:
    """
    Search corpus objects
    """
    struct = Struct(
        code=0,
        objects=[],
        count=0,
        total=0,
        errors=[],
    )

    model = models.Corpus
    dataset = sqlmodel.select(models.Corpus)  # default database query

    query_normalized = _query_normalize(query=query)

    struct_tokens = services.mql.Parse(query_normalized).call()

    for token in struct_tokens.tokens:
        value = token["value"]

        if token["field"] in ["id", "ids"]:
            # match query
            ids = [int(id.strip()) for id in value.split(",")]
            dataset = dataset.where(model.id.in_(ids))
        elif token["field"].startswith("name"):
            # like query
            value_normal = re.sub(r"~", "", value)
            dataset = dataset.where(model.name.like("%" + value_normal + "%"))
        elif token["field"] == "state":
            # match query
            dataset = dataset.where(model.state == value)

    struct.objects = db_session.exec(dataset.offset(offset).limit(limit).order_by(model.name.asc())).all()
    struct.count = len(struct.objects)
    struct.total = db_session.scalar(sqlmodel.select(sqlalchemy.func.count("*")).select_from(dataset.subquery()))

    return struct


def _query_normalize(query: str) -> str:
    """
    """
    if not query or (":" in query):
        return query

    return f"name:{query}"
