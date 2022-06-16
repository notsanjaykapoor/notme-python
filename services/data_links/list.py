import logging
import re
from dataclasses import dataclass

import sqlmodel
from sqlmodel.sql.expression import Select, SelectOfScalar

import models
import services.mql
from context import request_id

# this disables the warning: SAWarning: Class SelectOfScalar will not make use of SQL compilation caching
SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore


@dataclass
class Struct:
    code: int
    objects: list[models.Entity]
    count: int
    errors: list[str]


@dataclass
class StructToken:
    code: int
    tokens: list[dict]
    errors: list[str]


class List:
    def __init__(self, db: sqlmodel.Session, query: str = "", offset: int = 0, limit: int = 20):
        self._db = db
        self._query = query
        self._offset = offset
        self._limit = limit

        self._model = models.DataLink
        self._dataset = sqlmodel.select(self._model)  # default database query
        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        self._logger.info(f"{request_id.get()} {__name__} query {self._query}")

        # tokenize query

        struct_tokens = services.mql.Parse(self._query).call()

        self._logger.info(f"{request_id.get()} {__name__} tokens {struct_tokens.tokens}")

        for token in struct_tokens.tokens:
            value = token["value"]

            if token["field"] == "id":
                # match query
                self._dataset = self._dataset.where(self._model.id == value)
            elif token["field"] == "src_name":
                match = re.match(r"^~", value)

                if match:
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(self._model.src_name.like("%" + value_normal + "%"))  # type: ignore
                else:
                    # match query
                    self._dataset = self._dataset.where(self._model.src_name == value)
            elif token["field"] == "src_slug":
                match = re.match(r"^~", value)

                if match:
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(self._model.src_slug.like("%" + value_normal + "%"))  # type: ignore
                else:
                    # match query
                    self._dataset = self._dataset.where(self._model.src_slug == value)

        struct.objects = self._db.exec(self._dataset.offset(self._offset).limit(self._limit)).all()

        struct.count = len(struct.objects)

        return struct
