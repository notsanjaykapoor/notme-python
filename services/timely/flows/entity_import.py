import dataclasses
import json
import os
import sys
import typing

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import bytewax  # # noqa: E402
import bytewax.inputs  # # noqa: E402

import log  # noqa: E402
import services.database.session  # noqa: E402
import services.entities.operators  # noqa: E402
import services.graph.operators  # noqa: E402
import services.graph.session  # noqa: E402


@dataclasses.dataclass
class Struct:
    code: int
    errors: list[str]


class EntityImport:
    """
    timely dataflow to import entities
    """

    def __init__(self, file: str):
        self._file = file

        self._epoch = 1
        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [])

        flow_1 = bytewax.Dataflow()
        # flow_1.filter(self._entity_filter)
        flow_1.map(self._entity_sync)
        # {entity_id: "1XYZABC"}
        flow_1.map(self._graph_object_sync)
        # {entity_id: "1XYZABC", "nodes_created": 1, "edges_created": 1}
        flow_1.map(self._graph_geo_sync)
        # {entity_id: "1XYZABC", "nodes_created": 1, "edges_created": 1, "geo": 0|1}

        # flow_1.stateful_map("state_map", self._state_builder, self._state_mapper)

        flow_1.capture()

        flow_2 = bytewax.Dataflow()
        flow_2.capture()

        output_1 = bytewax.run(flow_1, self._input())

        for epoch, item in bytewax.run(flow_2, output_1):
            self._logger.info(f"flow_2 epoch {epoch} item {item}")

        return struct

    # example filter
    def _entity_filter(self, object: dict) -> bool:
        return object["id"] in ["01G5386HVMP79PKM21YJGMFG5K"]

    def _entity_sync(self, object: dict) -> dict:
        with services.database.session.get() as db:
            struct = services.entities.operators.ObjectSync(db=db, object=object).call()
            return {"entity_id": list(struct.entity_ids)[0], "entity_code": struct.code}

    def _graph_geo_sync(self, object: dict) -> dict:
        with services.database.session.get() as db, services.graph.session.get() as neo:
            struct = services.graph.operators.EntityLocationSync(db=db, neo=neo, entity_id=object["entity_id"]).call()
            object["geo"] = struct.geo
            return object

    def _graph_object_sync(self, object: dict) -> dict:
        object["nodes_created"] = 0
        object["nodes_deleted"] = 0
        object["edges_created"] = 0
        object["edges_deleted"] = 0

        with services.database.session.get() as db, services.graph.session.get() as neo:
            if object["entity_code"] in [200, 201]:
                struct = services.graph.operators.EntitySync(
                    db=db,
                    neo=neo,
                    entity_id=object["entity_id"],
                    entity_code=object["entity_code"],
                ).call()

                object["nodes_created"] = struct.nodes_created
                object["nodes_deleted"] = struct.nodes_deleted
                object["edges_created"] = struct.edges_created
                object["edges_deleted"] = struct.edges_deleted

            return object

    def _input(self) -> typing.Generator[tuple[int, dict], None, None]:
        objects = json.load(open(self._file))

        for object in objects:
            yield self._epoch, object

    def _state_builder(self, key):
        self._logger.info(f"state_builder key {key}")
        return set()

    def _state_mapper(self, key, item):
        self._logger.info(f"state_mapper key {key} item {item}")

        if item in key:
            return key, True
        else:
            return key, False
