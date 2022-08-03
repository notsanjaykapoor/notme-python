import dataclasses

import datadog
import neo4j
import sqlmodel

import services.graph
import services.graph.sync


@dataclasses.dataclass
class Struct:
    code: int
    nodes_created: int
    nodes: list[dict]
    edges_created: int
    edges: list[dict]
    errors: list[str]


class EntitySync:
    """
    sync entity to graph database
    """

    def __init__(self, db: sqlmodel.Session, neo: neo4j.Session, entity_id: str):
        self._db = db
        self._neo = neo
        self._entity_id = entity_id

    @datadog.statsd.timed(f"{__name__}.timer", tags=["env:dev"])
    def call(self) -> Struct:
        struct = Struct(0, 0, [], 0, [], [])

        entities = services.entities.get_all_by_id(db=self._db, id=self._entity_id)

        if not entities:
            struct.code = 404
            return struct

        for entity in entities:
            struct_node_entity = services.graph.sync.CreateNodeFromEntityId(
                neo=self._neo,
                entity=entity,
            ).call()

            struct.nodes_created += struct_node_entity.nodes_created
            struct.nodes += struct_node_entity.nodes

            struct_node_property = services.graph.sync.CreateNodeFromEntitySlug(
                db=self._db,
                neo=self._neo,
                entity=entity,
            ).call()

            struct.nodes_created += struct_node_property.nodes_created
            struct.nodes += struct_node_property.nodes

            struct_nodes_from_data_links = services.graph.sync.CreateNodesFromDataLinks(
                db=self._db,
                neo=self._neo,
                entity=entity,
            ).call()

            struct.nodes_created += struct_nodes_from_data_links.nodes_created
            struct.nodes += struct_nodes_from_data_links.nodes

            struct_edges_has = services.graph.sync.CreateEdgesHas(
                db=self._db,
                neo=self._neo,
                entity=entity,
            ).call()

            struct.edges_created += struct_edges_has.edges_created
            struct.edges += struct_edges_has.edges

        # once nodes have been created, check entities for any nodes based on data links and create edges

        for entity in entities:
            struct_edges_from_links = services.graph.sync.CreateEdgesFromDataLinks(
                db=self._db,
                neo=self._neo,
                entity=entity,
            ).call()

            struct.edges_created += struct_edges_from_links.edges_created
            struct.edges += struct_edges_from_links.edges

        # print(struct)  # xxx

        return struct
