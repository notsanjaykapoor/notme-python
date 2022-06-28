import dataclasses
import re

import sqlmodel

import log
import models
import services.mql
from context import request_id


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

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        self._logger.info(f"{request_id.get()} {__name__} query {self._query}")

        # tokenize query

        struct_tokens = services.mql.Parse(self._query).call()

        self._logger.info(f"{request_id.get()} {__name__} tokens {struct_tokens.tokens}")

        for token in struct_tokens.tokens:
            value = token["value"]

            if token["field"] == "user_id":
                match = re.match(r"^~", value)

                if match:
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(self._model.user_id.like("%" + value_normal + "%"))  # type: ignore
                else:
                    # match query
                    self._dataset = self._dataset.where(self._model.user_id == value)

        struct.objects = self._db.exec(self._dataset.offset(self._offset).limit(self._limit)).all()
        struct.count = len(struct.objects)

        return struct
