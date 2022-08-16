import dataclasses
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import bytewax  # noqa: E402
import bytewax.inputs  # noqa: E402
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


class EntityDbSync:
    """
    timely dataflow to sync entity objects to database
    """

    def __init__(self, input: list[tuple[int, dict]], db: sqlmodel.Session):
        self._input = input
        self._db = db

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [], [])

        flow_1 = bytewax.Dataflow()
        # {'person.email': {'value': 'user1@gmail.com', 'type': 'string', 'pk': 1}}}
        flow_1.map(self._map_entity_id_resolve)
        # {'person.email': {'value': 'user1@gmail.com', 'type': 'string', 'pk': 1}}, 'person.id': {'value': '123'}, 'code': 200|201|409}
        flow_1.map(self._map_entity_build)
        # {'entities': []}
        flow_1.map(self._map_entity_persist)
        # {'entity_id': '01GAFJ1MBB1V4TF7AGVQKN4GEK', 'entity_code': 201}
        flow_1.capture()

        struct.output = bytewax.run(flow_1, self._input)

        return struct

    def _entity_id_key(self, object: dict) -> str:
        entity_name = self._entity_name(object)
        return f"{entity_name}._id"

    def _entity_name(self, object: dict) -> str:
        object_keys = list(object.keys())
        entity_name, _ = object_keys[0].split(".")
        return entity_name

    def _map_entity_id_resolve(self, object: dict) -> dict:
        """check pk and get/create id field"""
        struct_resolve = services.entities.operators.IdResolve(db=self._db, object=object).call()

        entity_id_key = self._entity_id_key(object)

        object[entity_id_key] = {
            "value": struct_resolve.id,
            "type": "string",
            "code": struct_resolve.code,
        }

        return object

    def _map_entity_build(self, object: dict) -> dict:
        entity_id_key = self._entity_id_key(object)

        object_id = object[entity_id_key]

        if object_id["code"] in [200, 409]:
            entity_id = object_id["value"]

            struct_list = services.entities.List(
                db=self._db,
                query=f"entity_id:{entity_id}",
                offset=0,
                limit=1024,
            ).call()

            if object_id["code"] == 200:
                pass  # todo

            return {"code": object_id["code"], "entities": struct_list.objects}
        elif object_id["code"] == 201:
            struct_build = services.entities.operators.EntityBuild(db=self._db, object=object).call()

            return {"code": object_id["code"], "entities": struct_build.entities}

        return object

    def _map_entity_persist(self, object: dict) -> dict:
        struct_persist = services.entities.operators.EntityPersist(
            db=self._db,
            entities=object["entities"],
        ).call()

        return {"code": struct_persist.code, "entity_id": list(struct_persist.entity_ids)[0]}
