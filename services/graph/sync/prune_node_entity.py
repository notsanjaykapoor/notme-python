import dataclasses

import datadog
import neo4j
import neo4j.graph
import sqlmodel

import log
import models
import services.graph.query
import services.graph.query.types
import services.graph.tx


@dataclasses.dataclass
class Struct:
    code: int
    nodes_deleted: int
    edges_deleted: int
    errors: list[str]


class PruneNodeEntity:
    """
    prune entity node edges
    """

    def __init__(self, db: sqlmodel.Session, neo: neo4j.Session, entity: models.Entity):
        self._db = db
        self._neo = neo
        self._entity = entity

        self._entity_id = self._entity.entity_id
        self._entity_labels = f"{self._entity.entity_name}:{models.entity.LABEL_ENTITY}"

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, 0, [])

        struct_list = services.entities.List(
            db=self._db,
            query=f"entity_id:{self._entity_id} state:active",
            offset=0,
            limit=1024,
        ).call()

        entities = struct_list.objects

        self._logger.info(f"{__name__} entity {self._entity_labels} id {self._entity_id} objects {len(entities)}")

        graph_query = self._query_node_edges()

        with datadog.statsd.timed("neo.writer", tags=[f"writer:{__name__}"]):
            records = self._neo.read_transaction(services.graph.tx.read, graph_query.query, graph_query.params)

        record_props = [record for record in records if models.entity.LABEL_PROPERTY in record["node"].labels]
        record_links = [record for record in records if models.entity.LABEL_LINK in record["node"].labels]

        # find entity properties that no longer exist
        record_props_deleted = [record for record in record_props if self._node_property_deleted(node=record["node"], entities=entities) == 1]
        record_links_deleted = []

        # find related entity links that no longer exist
        for record_prop_deleted in record_props_deleted:
            property = record_prop_deleted["node"].get("id")
            for record_link in record_links:
                if self._node_link_deleted(node=record_link["node"], property=property) == 1:
                    record_links_deleted.append(record_link)

        # delete graph edges

        for record in record_props_deleted:
            graph_query = self._query_edge_delete(node=record["node"])

            with datadog.statsd.timed("neo.writer", tags=[f"writer:{__name__}"]):
                summary = self._neo.write_transaction(services.graph.tx.write, graph_query.query, graph_query.params)
                struct.edges_deleted += summary.counters.relationships_deleted

        for record in record_links_deleted:
            graph_query = self._query_edge_delete(node=record["node"])

            with datadog.statsd.timed("neo.writer", tags=[f"writer:{__name__}"]):
                summary = self._neo.write_transaction(services.graph.tx.write, graph_query.query, graph_query.params)
                struct.edges_deleted += summary.counters.relationships_deleted

        return struct

    def _node_link_deleted(self, node: neo4j.graph.Node, property: str) -> int:
        """
        returns 1 if link node is related to the property that has been deleted

        node: link node with id property, e.g. case_jacket_id:person_record_id:1001
        property: entity property that has been deleted, e.g record_id:1000
        """

        src_name, dst_name, obj_value = node.get("id").split(":")
        lnk_name, lnk_value = f"{self._entity.entity_name}_{property}".split(":")

        if lnk_value != obj_value:
            return 0

        if (src_name == lnk_name) or (dst_name == lnk_name):
            # matching link node that should be deleted
            return 1

        return 0

    def _node_property_deleted(self, node: neo4j.graph.Node, entities: list[models.Entity]) -> int:
        "returns 1 if property node has been deleted from entity in database"

        entity_slug, entity_value = node.get("id").split(":")

        # find matching entity

        entities_matched = [entity for entity in entities if (entity.slug == entity_slug and entity.type_value == entity_value)]

        if not entities_matched:
            # property has been deleted
            return 1

        return 0

    def _query_edge_delete(self, node: neo4j.graph.Node) -> services.graph.query.types.GraphQuery:
        struct = services.graph.query.types.GraphQuery("", {})

        dst_id = node.get("id")
        dst_label = ":".join(list(node.labels))

        struct.query = f"match(s:{self._entity_labels} {{id: $src_id}})-[edge]-(d:{dst_label} {{id: $dst_id}}) delete edge"
        struct.params = {"src_id": self._entity_id, "dst_id": dst_id}

        return struct

    def _query_node_edges(self) -> services.graph.query.types.GraphQuery:
        struct = services.graph.query.types.GraphQuery("", {})

        struct.query = f"match(n:{self._entity_labels} {{id: $id}})-[edge]-(node) return node,edge"
        struct.params = {"id": self._entity_id}

        return struct
