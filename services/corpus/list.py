import dataclasses
import re

import sqlalchemy
import sqlmodel

import models
import services.corpus

@dataclasses.dataclass
class Struct:
    code: int
    objects: list[models.User]
    count: int
    errors: list[str]


def list_all(db: sqlmodel.Session, query: str = "", offset: int = 0, limit: int = 20) -> Struct:
    """
    List all corpus collections
    """
    struct = Struct(0, [], 0, [])

    model = models.User
    dataset = sqlmodel.select(models.User)  # default database query

    struct_tokens = services.mql.Parse(query).call()

    for token in struct_tokens.tokens:
        value = token["value"]

        if token["field"] == "email":
            # match query
            dataset = dataset.where(model.email == value)
        elif token["field"] == "user_id":
            if re.match(r"^~", value):
                # like query
                value_normal = re.sub(r"~", "", value)
                dataset = dataset.where(model.user_id.like("%" + value_normal + "%"))  # type: ignore
            else:
                # match query
                dataset = dataset.where(model.user_id == value)

    struct.objects = db.exec(dataset.offset(offset).limit(limit)).all()
    struct.count = len(struct.objects)

    return struct


