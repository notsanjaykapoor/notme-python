import dataclasses

import neo4j
import sqlmodel
from sqlmodel.sql.expression import Select, SelectOfScalar

import context
import gql.types
import log
import services.graph.tx
import services.mql

# this disables the warning: SAWarning: Class SelectOfScalar will not make use of SQL compilation caching
SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore


@dataclasses.dataclass
class Struct:
    code: int
    objects: list[gql.types.GqlNode]
    count: int
    errors: list[str]


class List:
    def __init__(self, db: sqlmodel.Session, neo: neo4j.Session, query: str = "", offset: int = 0, limit: int = 100):
        self._db = db
        self._neo = neo
        self._query = query
        self._offset = offset
        self._limit = limit

        # self._model = models.EntityNode
        # self._dataset = sqlmodel.select(models.EntityNode)  # default database query

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        self._logger.info(f"{context.rid_get()} {__name__} query {self._query}")

        # tokenize query

        struct_tokens = services.mql.Parse(self._query).call()

        self._logger.info(f"{context.rid_get()} {__name__} tokens {struct_tokens.tokens}")

        struct_graph = services.graph.query.match_all()

        self._logger.info(f"{context.rid_get()} {__name__} query {struct_graph.query}")

        records = self._neo.read_transaction(services.graph.tx.read, struct_graph.query, struct_graph.params)

        for record in records:
            node = record["n"]
            struct.objects.append(
                gql.types.GqlNode(  # type: ignore
                    id=node.get("id"),
                    name=node.get("name", ""),
                    labels=[label for label in node.labels],
                )
            )

        # for token in struct_tokens.tokens:
        #     value = token["value"]

        # struct.objects = self._db.exec(self._dataset.offset(self._offset).limit(self._limit)).all()

        struct.count = len(struct.objects)

        return struct
