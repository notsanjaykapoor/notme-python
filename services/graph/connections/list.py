import logging
import re
import typing

from dataclasses import dataclass
from sqlmodel import select, Session

from sqlmodel.sql.expression import Select, SelectOfScalar

SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

import models
import services.mql

from context import request_id


@dataclass
class Struct:
    code: int
    objects: typing.List[models.GraphConnectionEntity]
    objects_count: int
    errors: typing.List[str]


@dataclass
class StructToken:
    code: int
    tokens: list[dict]
    errors: list[str]


class List:
    def __init__(self, db: Session, query: str = "", offset: int = 0, limit: int = 20):
        self._db = db
        self._query = query
        self._offset = offset
        self._limit = limit

        self._dataset = select(models.GraphConnectionEntity)  # default database query
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

            if token["field"] == "entity_name":
                match = re.match(r"^~", value)

                if match:
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(
                        models.GraphConnectionEntity.entity_name.like("%" + value_normal + "%")  # type: ignore
                    )
                else:
                    # match query
                    self._dataset = self._dataset.where(
                        models.GraphConnectionEntity.entity_name == value
                    )
            elif token["field"] == "entity_slug":
                match = re.match(r"^~", value)

                if match:
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(
                        models.GraphConnectionEntity.entity_slug.like("%" + value_normal + "%")  # type: ignore
                    )
                else:
                    # match query
                    self._dataset = self._dataset.where(
                        models.GraphConnectionEntity.entity_slug == value
                    )
            elif token["field"] == "id":
                self._dataset = self._dataset.where(
                    models.GraphConnectionEntity.id == value
                )

        struct.objects = self._db.exec(
            self._dataset.offset(self._offset).limit(self._limit)
        ).all()

        struct.objects_count = len(struct.objects)

        return struct
