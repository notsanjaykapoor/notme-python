import dataclasses
import re

import datadog
import sqlmodel

import context
import log
import models
import services.mql


@dataclasses.dataclass
class Struct:
    code: int
    objects: list[models.User]
    count: int
    errors: list[str]


class List:
    def __init__(self, db: sqlmodel.Session, query: str = "", offset: int = 0, limit: int = 20):
        self._db = db
        self._query = query
        self._offset = offset
        self._limit = limit

        self._model = models.User
        self._dataset = sqlmodel.select(models.User)  # default database query
        self._logger = log.init("service")

    @datadog.statsd.timed("service", tags=[f"service:{__name__}"])
    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        self._logger.info(f"{context.rid_get()} {__name__} query {self._query}")

        # tokenize query

        struct_tokens = services.mql.Parse(self._query).call()

        self._logger.info(f"{context.rid_get()} {__name__} tokens {struct_tokens.tokens}")

        for token in struct_tokens.tokens:
            value = token["value"]

            if token["field"] == "email":
                # match query
                self._dataset = self._dataset.where(self._model.email == value)
            elif token["field"] == "user_id":
                if re.match(r"^~", value):
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(self._model.user_id.like("%" + value_normal + "%"))  # type: ignore
                else:
                    # match query
                    self._dataset = self._dataset.where(self._model.user_id == value)

        struct.objects = self._db.exec(self._dataset.offset(self._offset).limit(self._limit)).all()
        struct.count = len(struct.objects)

        return struct
