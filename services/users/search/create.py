import dataclasses

import typesense

import context
import log
import models


@dataclasses.dataclass
class Struct:
    code: int
    errors: list[str]


class Create:
    def __init__(self, ts_client: typesense.client.Client):
        self._ts_client = ts_client

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [])

        self._logger.info(f"{context.rid_get()} {__name__}")

        self._create_schema(
            name=models.User.typesense_collection(),
            schema=models.User.typesense_schema(),
        )

        return struct

    def _create_schema(self, name: str, schema: dict):
        names = [
            collection["name"] for collection in self._ts_client.collections.retrieve()
        ]

        if name in names:
            self._ts_client.collections[name].delete()

        self._ts_client.collections.create(schema)
