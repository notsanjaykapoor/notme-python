import logging
import re
import sqlmodel

from dataclasses import dataclass

from sqlmodel.sql.expression import Select, SelectOfScalar

SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

import models
import services.mql

from context import request_id


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
    def __init__(
        self, db: sqlmodel.Session, query: str = "", offset: int = 0, limit: int = 20
    ):
        self._db = db
        self._query = query
        self._offset = offset
        self._limit = limit

        self._model = models.DataModel
        self._dataset = sqlmodel.select(models.DataModel)  # default database query
        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        self._logger.info(f"{request_id.get()} {__name__} query {self._query}")

        # tokenize query

        struct_tokens = services.mql.Parse(self._query).call()

        self._logger.info(
            f"{request_id.get()} {__name__} tokens {struct_tokens.tokens}"
        )

        for token in struct_tokens.tokens:
            value = token["value"]

            if token["field"] == "id":
                # match query
                self._dataset = self._dataset.where(self._model.id == value)
            elif token["field"] == "name":
                match = re.match(r"^~", value)

                if match:
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(
                        self._model.object_name.like("%" + value_normal + "%")  # type: ignore
                    )
                else:
                    # match query
                    self._dataset = self._dataset.where(
                        self._model.object_name == value
                    )
            elif token["field"] == "slug":
                match = re.match(r"^~", value)

                if match:
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(
                        self._model.object_slug.like("%" + value_normal + "%")  # type: ignore
                    )
                else:
                    # match query
                    self._dataset = self._dataset.where(
                        self._model.object_slug == value
                    )
            elif token["field"] == "type":
                match = re.match(r"^~", value)

                if match:
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(
                        self._model.object_type.like("%" + value_normal + "%")  # type: ignore
                    )
                else:
                    # match query
                    self._dataset = self._dataset.where(
                        self._model.object_type == value
                    )

        struct.objects = self._db.exec(
            self._dataset.offset(self._offset).limit(self._limit)
        ).all()

        struct.count = len(struct.objects)

        return struct
