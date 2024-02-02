import dataclasses
import re

import sqlalchemy
import sqlmodel
from sqlmodel.sql.expression import Select, SelectOfScalar

import context
import log
import models
import services.mql

# this disables the warning: SAWarning: Class SelectOfScalar will not make use of SQL compilation caching
SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore


@dataclasses.dataclass
class Struct:
    code: int
    objects: list[models.Entity]
    count: int
    errors: list[str]


class List:
    def __init__(self, db: sqlmodel.Session, query: str = "", offset: int = 0, limit: int = 100):
        self._db = db
        self._query = query
        self._offset = offset
        self._limit = limit

        self._model = models.Entity
        self._dataset = sqlmodel.select(models.Entity)  # default database query
        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        self._logger.info(f"{context.rid_get()} {__name__} query {self._query}")

        # tokenize query

        struct_tokens = services.mql.Parse(self._query).call()

        self._logger.info(f"{context.rid_get()} {__name__} tokens {struct_tokens.tokens}")

        for token in struct_tokens.tokens:
            value = token["value"]

            if token["field"] == "entity_id":
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
            elif token["field"] == "entity_key":
                match = re.match(r"^~", value)

                if match:
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(self._model.entity_key.like("%" + value_normal + "%"))  # type: ignore
                else:
                    # match query
                    self._dataset = self._dataset.where(self._model.entity_key == value)
            elif token["field"] == "entity_name":
                if re.match(r"^~", value):
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(self._model.entity_name.like("%" + value_normal + "%"))  # type: ignore
                else:
                    # match query
                    self._dataset = self._dataset.where(self._model.entity_name == value)
            elif token["field"] == "name":
                if re.match(r"^~", value):
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(self._model.name.like("%" + value_normal + "%"))  # type: ignore
                else:
                    # equal query
                    self._dataset = self._dataset.where(self._model.name == value)
            elif token["field"] == "name_text":
                # full text search
                ts_vector = sqlalchemy.func.to_tsvector(models.Entity.name)
                self._dataset = self._dataset.where(ts_vector.match(value))
                # self._dataset = self._dataset.where(ts_vector.match(sqlalchemy.func.websearch_to_tsquery(value)))
            elif token["field"] == "node":
                # match query
                self._dataset = self._dataset.where(self._model.node == value)
            elif token["field"] == "slug":
                if re.match(r"^~", value):
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(self._model.slug.like("%" + value_normal + "%"))  # type: ignore
                else:
                    # equal query
                    self._dataset = self._dataset.where(models.Entity.slug == value)
            elif token["field"] == "state":
                # match query
                self._dataset = self._dataset.where(self._model.state == value)
            elif token["field"] == "tags":
                # like query
                value_format = f"|{value}|"
                self._dataset = self._dataset.where(self._model.tags.like("%" + value_format + "%"))  # type: ignore
            elif token["field"] == "type_value":
                if re.match(r"^~", value):
                    # like query
                    value_normal = re.sub(r"~", "", value)
                    self._dataset = self._dataset.where(self._model.type_value.like("%" + value_normal + "%"))  # type: ignore
                else:
                    # equal query
                    self._dataset = self._dataset.where(self._model.type_value == value)

        struct.objects = self._db.exec(self._dataset.offset(self._offset).limit(self._limit)).all()

        struct.count = len(struct.objects)

        return struct
