import dataclasses

import neo4j
import sqlmodel

import log
import models
import services.entities
import services.entity_locations
import services.graph
import services.graph.sync


@dataclasses.dataclass
class Struct:
    code: int
    geo: int
    nodes_updated: int
    errors: list[str]


class EntityLocationSync:
    """
    sync entity location object with graph database
    """

    def __init__(self, db: sqlmodel.Session, neo: neo4j.Session, entity_id: str):
        self._db = db
        self._neo = neo
        self._entity_id = entity_id

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, 0, [])

        # check entity location
        struct_list = services.entity_locations.List(
            db=self._db,
            query=f"entity_id:{self._entity_id}",
            offset=0,
            limit=1,
        ).call()

        if struct_list.count == 0:
            struct.code = 422

            return struct

        # validate entity
        entities = services.entities.get_all_by_ids(db=self._db, ids=[self._entity_id])

        if not entities:
            struct.code = 404
            return struct

        struct.geo = 1

        # update graph database
        struct.nodes_updated += self._node_geo_update(
            entity_name=entities[0].entity_name,
            entity_location=struct_list.objects[0],
        )

        return struct

    def _node_geo_update(self, entity_name: str, entity_location: models.EntityLocation) -> int:
        query_update = f"""
        match(n:{entity_name} {{id: $id}}) set n.location = point({{latitude: $lat, longitude: $lon}})
        """

        point = entity_location.point

        params = {"id": self._entity_id, "lat": point.y, "lon": point.x}

        self._logger.info(f"{__name__} label '{entity_name}' props {params}")

        self._neo.write_transaction(services.graph.tx.write, query_update, params)

        return 1
