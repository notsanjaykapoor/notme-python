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
    def __init__(self, db: sqlmodel.Session, query: str = "", offset: int = 0, limit: int = 100):
        self._db = db
        self._query = query
        self._offset = offset
        self._limit = limit

        self._model = models.Entity
        self._dataset = sqlmodel.select(models.Entity)  # default database query
        self._logger = logging.getLogger("api")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        self._logger.info(f"{request_id.get()} {__name__} query {self._query}")

        # tokenize query

        struct_tokens = services.mql.Parse(self._query).call()

        self._logger.info(f"{request_id.get()} {__name__} tokens {struct_tokens.tokens}")

        for token in struct_tokens.tokens:
            value = token["value"]

            if token["field"] == "entity_id":
                # match = re.match(r"^~", value)

                if match := re.match(r"^~", value):
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(self._model.entity_id.like("%" + value_normal + "%"))  # type: ignore
                elif match := re.match(r"\S+\|\S+", value):
                    values = value.split("|")
                    self._dataset = self._dataset.where(self._model.entity_id.in_(values))  # type: ignore
                else:
                    # match query
                    self._dataset = self._dataset.where(self._model.entity_id == value)
            elif token["field"] == "entity_name":
                match = re.match(r"^~", value)

                if match:
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(self._model.entity_name.like("%" + value_normal + "%"))  # type: ignore
                else:
                    # match query
                    self._dataset = self._dataset.where(self._model.entity_name == value)
            elif token["field"] == "slug":
                match = re.match(r"^~", value)

                if match:
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(self._model.slug.like("%" + value_normal + "%"))  # type: ignore
                else:
                    # match query
                    self._dataset = self._dataset.where(models.Entity.slug == value)
            elif token["field"] == "type_value":
                match = re.match(r"^~", value)

                if match:
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(self._model.type_value.like("%" + value_normal + "%"))  # type: ignore
                else:
                    # match query
                    self._dataset = self._dataset.where(self._model.type_value == value)

        struct.objects = self._db.exec(self._dataset.offset(self._offset).limit(self._limit)).all()

        struct.count = len(struct.objects)

        return struct
