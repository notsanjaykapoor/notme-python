import dataclasses
import re

import sqlmodel

import context
import log
import models
import services.mql


@dataclasses.dataclass
class Struct:
    code: int
    objects: list[models.EntityWatch]
    count: int
    errors: list[str]


class List:
    def __init__(self, db: sqlmodel.Session, query: str = "", offset: int = 0, limit: int = 100):
        self._db = db
        self._query = query
        self._offset = offset
        self._limit = limit

        self._model = models.EntityWatch
        self._dataset = sqlmodel.select(models.EntityWatch)  # default database query
        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        self._logger.info(f"{context.rid_get()} {__name__} query {self._query}")

        # tokenize query

        struct_tokens = services.mql.Parse(self._query).call()

        self._logger.info(f"{context.rid_get()} {__name__} tokens {struct_tokens.tokens}")

        for token in struct_tokens.tokens:
            field = token["field"]
            value = token["value"]

            if field == "topic":
                if re.match(r"^~", value):
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(self._model.topic.like("%" + value_normal + "%"))  # type: ignore
                elif re.match(r"\S+\|\S+", value):
                    values = value.split("|")
                    self._dataset = self._dataset.where(self._model.topic.in_(values))  # type: ignore
                else:
                    # match query
                    self._dataset = self._dataset.where(self._model.topic == value)

        struct.objects = self._db.exec(self._dataset.offset(self._offset).limit(self._limit)).all()

        struct.count = len(struct.objects)

        return struct
