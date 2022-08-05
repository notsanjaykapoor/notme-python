import dataclasses

import datadog
import neo4j
import sqlmodel

import services.entities
import services.graph
import services.graph.sync


@dataclasses.dataclass
class Struct:
    code: int
    nodes_deleted: int
    nodes_created: int
    nodes: list[dict]
    edges_created: int
    edges_deleted: int
    edges: list[dict]
    errors: list[str]


class EntitySync:
    """
    sync entity to graph database
    """

    def __init__(self, db: sqlmodel.Session, neo: neo4j.Session, entity_id: str, entity_code: int):
        self._db = db
        self._neo = neo
        self._entity_id = entity_id
        self._entity_code = entity_code

    @datadog.statsd.timed(f"{__name__}.timer", tags=["env:dev"])
    def call(self) -> Struct:
        struct = Struct(0, 0, 0, [], 0, 0, [], [])

        if self._entity_code not in [200, 201]:
            struct.code = 422
            return struct

        struct_list = services.entities.List(
            db=self._db,
            query=f"entity_id:{self._entity_id} state:active",
            offset=0,
            limit=1024,
        ).call()

        entities = struct_list.objects

        if not entities:
            struct.code = 404
            return struct

        for entity in entities:
            # create entity nodes

            create_node_entity_id = services.graph.sync.CreateNodeEntity(
                neo=self._neo,
                entity=entity,
            ).call()

            struct.nodes_created += create_node_entity_id.nodes_created

            create_node_property = services.graph.sync.CreateNodeProperty(
                db=self._db,
                neo=self._neo,
                entity=entity,
            ).call()

            struct.nodes_created += create_node_property.nodes_created

            create_nodes_links = services.graph.sync.CreateNodesLink(
                db=self._db,
                neo=self._neo,
                entity=entity,
            ).call()

            struct.nodes_created += create_nodes_links.nodes_created

            # create entity node edge(s) (has edge)

            create_edges_has = services.graph.sync.CreateEdgesHas(
                db=self._db,
                neo=self._neo,
                entity=entity,
            ).call()

            struct.edges_created += create_edges_has.edges_created
            struct.edges += create_edges_has.edges

        # once all nodes have been created, create edges from entity nodes to any data links

        for entity in entities:
            create_edges_from_links = services.graph.sync.CreateEdgesFromDataLinks(
                db=self._db,
                neo=self._neo,
                entity=entity,
            ).call()

            struct.edges_created += create_edges_from_links.edges_created
            struct.edges += create_edges_from_links.edges

        # check entity and prune old edges

        prune_edges = services.graph.sync.PruneNodeEntity(
            db=self._db,
            neo=self._neo,
            entity=entities[0],
        ).call()

        struct.edges_deleted += prune_edges.edges_deleted

        prune_nodes = services.graph.sync.PruneNodeUnconnected(
            neo=self._neo,
            entity=entities[0],
        ).call()

        struct.nodes_deleted += prune_nodes.nodes_deleted

        return struct
