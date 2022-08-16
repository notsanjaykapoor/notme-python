import dataclasses
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import bytewax  # noqa: E402
import bytewax.inputs  # noqa: E402
import neo4j  # noqa: E402
import sqlmodel  # noqa: E402

import log  # noqa: E402
import services.entities  # noqa: E402
import services.entities.operators  # noqa: E402
import services.graph.operators  # noqa: E402
import services.graph.session  # noqa: E402


@dataclasses.dataclass
class Struct:
    code: int
    output: list[tuple[int, dict]]
    errors: list[str]


class EntityGraphSync:
    """
    timely dataflow to sync entity objects to graph database
    """

    def __init__(self, input: list[tuple[int, dict]], db: sqlmodel.Session, neo: neo4j.Session):
        self._input = input
        self._db = db
        self._neo = neo

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [], [])

        flow_1 = bytewax.Dataflow()
        # {'code': 201, 'entity_id': '01GAKG7TGFCTSAVZ6PKV83V85C'}
        flow_1.map(self._graph_object_sync)
        # {'code': 201, 'entity_id': "1XYZABC", "nodes_created": 1, "edges_created": 1}
        flow_1.map(self._graph_geo_sync)
        # {'code': 201, entity_id: "1XYZABC", "nodes_created": 1, "edges_created": 1, "geo": 0|1}
        flow_1.capture()

        struct.output = bytewax.run(flow_1, self._input)

        return struct

    def _graph_geo_sync(self, object: dict) -> dict:
        struct = services.graph.operators.EntityLocationSync(
            db=self._db,
            neo=self._neo,
            entity_id=object["entity_id"],
        ).call()
        object["geo"] = struct.geo
        return object

    def _graph_object_sync(self, object: dict) -> dict:
        object["nodes_created"] = 0
        object["nodes_deleted"] = 0
        object["edges_created"] = 0
        object["edges_deleted"] = 0

        if object["code"] in [200, 201]:
            struct = services.graph.operators.GraphSync(
                db=self._db,
                neo=self._neo,
                entity_id=object["entity_id"],
                entity_code=object["code"],
            ).call()

            object["nodes_created"] = struct.nodes_created
            object["nodes_deleted"] = struct.nodes_deleted
            object["edges_created"] = struct.edges_created
            object["edges_deleted"] = struct.edges_deleted

        return object
