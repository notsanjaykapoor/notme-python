import dataclasses
import datetime
import re

import sqlalchemy
import sqlmodel

import models
import services.mql

@dataclasses.dataclass
class Struct:
    code: int
    objects: list[models.WorkQueue]
    count: int
    total: int
    errors: list[str]


def list(db_session: sqlmodel.Session, query: str, offset: int, limit: int) -> Struct:
    struct = Struct(
        code=0,
        objects=[],
        count=0,
        total=0,
        errors=[],
    )

    model = models.WorkQueue
    dataset = sqlmodel.select(model)

    query_normalized = _query_normalize(query=query)

    struct_tokens = services.mql.Parse(query_normalized).call()

    for token in struct_tokens.tokens:
        value = token["value"]

        if token["field"] == "completed_at":
            if re.match(r"^<", value):
                value_normal = re.sub(r"<", "", value)
                dataset = dataset.where(model.completed_at < datetime.datetime.fromtimestamp(int(value_normal)))
            elif re.match(r"^>", value):
                value_normal = re.sub(r">", "", value)
                dataset = dataset.where(model.completed_at > datetime.datetime.fromtimestamp(int(value_normal)))
        elif token["field"] == "name":
            if re.match(r"^~", value):
                # like query
                value_normal = re.sub(r"~", "", value)
                dataset = dataset.where(model.name.like("%" + value_normal + "%"))  # type: ignore
            else:
                # match query
                dataset = dataset.where(model.name == value)
        elif token["field"] == "partition":
            dataset = dataset.where(model.partition == value)
        elif token["field"] == "state":
            dataset = dataset.where(model.state == value)

    struct.objects = db_session.exec(dataset.offset(offset).limit(limit).order_by(model.id.desc())).all()
    struct.count = len(struct.objects)
    struct.total = db_session.scalar(sqlmodel.select(sqlalchemy.func.count("*")).select_from(dataset.subquery()))

    return struct


def _query_normalize(query: str) -> str:
    """
    """
    if not query or (":" in query):
        return query

    return f"name:~{query.replace('~', '')}"

