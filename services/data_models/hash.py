import dataclasses

import sqlmodel

import context
import log
import models
import services.data_models


@dataclasses.dataclass
class Struct:
    code: int
    object: dict
    errors: list[str]


class Hash:
    """return hashed object mapping datamodel keys (name and slug) to datamodels"""

    def __init__(self, db: sqlmodel.Session, query: str = ""):
        self._db = db
        self._query = query

        self._model = models.DataModel
        self._dataset = sqlmodel.select(models.DataModel)  # default database query

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, {}, [])

        self._logger.info(f"{context.rid_get()} {__name__} query {self._query}")

        # get list of data models

        struct_list = services.data_models.List(db=self._db, query=self._query, offset=0, limit=1024).call()

        # map list to hash keyed on [object_name, object_slug]

        for data_model in struct_list.objects:
            key = f"{data_model.object_name}:{data_model.object_slug}"

            struct.object[key] = data_model

        return struct
