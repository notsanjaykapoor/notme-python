import dataclasses
import re

import sqlmodel

import models
import services.corpus
import services.mql

@dataclasses.dataclass
class Struct:
    code: int
    objects: list[models.User]
    count: int
    errors: list[str]


def list_(db_session: sqlmodel.Session, query: str = "", offset: int = 0, limit: int = 20) -> Struct:
    """
    List all corpus collections
    """
    struct = Struct(0, [], 0, [])

    model = models.Corpus
    dataset = sqlmodel.select(models.Corpus)  # default database query

    struct_tokens = services.mql.Parse(query).call()

    for token in struct_tokens.tokens:
        value = token["value"]

        if token["field"].startswith("collection"):
            if re.match(r"^~", value):
                # like query
                value_normal = re.sub(r"~", "", value)
                dataset = dataset.where(model.collection_name.like("%" + value_normal + "%"))  # type: ignore
            else:
                # match query
                dataset = dataset.where(model.collection_name == value)
        elif token["field"] == "state":
            # match query
            dataset = dataset.where(model.state == value)

    struct.objects = db_session.exec(dataset.offset(offset).limit(limit).order_by(model.collection_name.asc())).all()
    struct.count = len(struct.objects)

    return struct


