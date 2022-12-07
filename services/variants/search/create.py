import dataclasses
import os

import sqlmodel
import typesense

import context
import log
import models


@dataclasses.dataclass
class Struct:
    code: int
    errors: list[str]


class Create:
    def __init__(self, search_client: typesense.client.Client):
        self._search_client = search_client

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [])

        self._logger.info(f"{context.rid_get()} {__name__}")

        self._create_schema(
            name=models.VariantPruleSchema.typesense_collection(),
            schema=models.VariantPruleSchema.typesense_schema(),
        )

        self._create_schema(
            name=models.VariantVruleSchema.typesense_collection(),
            schema=models.VariantVruleSchema.typesense_schema(),
        )

        return struct

    def _create_schema(self, name: str, schema: dict):
        names = [collection["name"] for collection in self._search_client.collections.retrieve()]

        if name in names:
            self._search_client.collections[name].delete()

        self._search_client.collections.create(schema)
