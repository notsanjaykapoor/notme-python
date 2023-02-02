import dataclasses

import sqlmodel
import typesense

import context
import log
import models


@dataclasses.dataclass
class Struct:
    code: int
    count: int
    errors: list[str]


class Index:
    def __init__(self, db: sqlmodel.Session, ts_client: typesense.client.Client):
        self._db = db
        self._ts_client = ts_client

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        self._logger.info(f"{context.rid_get()} {__name__}")

        struct.count += self._index_users()

        return struct

    def _index_users(self) -> int:
        """index users"""
        count = 0

        collection_name = models.User.typesense_collection()

        for user in self._users():
            self._ts_client.collections[collection_name].documents.create(
                user.typesense_document()
            )

            count += 1

            self._logger.info(
                f"{context.rid_get()} {__name__} collection {collection_name} user '{user.id}'"
            )

        return count

    def _users(self) -> list[models.User]:
        dataset = sqlmodel.select(
            models.User,
        )

        return self._db.exec(dataset).all()
