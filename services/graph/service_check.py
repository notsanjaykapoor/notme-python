import sqlmodel

import dot_init  # noqa: F401
import services.data_links
import services.data_models
import services.database.session
import services.entities
import services.entity_locations
import services.graph.query
import services.graph.session

CHECK_NAME = "notme.service_check"
CHECK_TAGS = ["check:graph-sync"]


def service_check() -> int:
    """check graph health"""

    with services.database.session.get() as db, services.graph.session.get() as neo:
        # database entity id count should match graph node count

        db_entity_count = _db_entity_count(db)

        struct_graph = services.graph.query.match_node_count()
        records = services.graph.query.execute(struct_graph.query, struct_graph.params, neo)

        graph_node_count = records[0]["count"]

        print(f"db_entity_count {db_entity_count} graph_node_count {graph_node_count}")

        if db_entity_count != graph_node_count:
            _metric(status=2, message="graph sync error")

        db_relationship_count = _db_relationship_count(db)

        struct_graph = services.graph.query.match_edges_count(names="has")
        records = services.graph.query.execute(struct_graph.query, struct_graph.params, neo)

        graph_rel_has_count = records[0]["count"]

        struct_graph = services.graph.query.match_edges_count(names="linked")
        records = services.graph.query.execute(struct_graph.query, struct_graph.params, neo)

        graph_rel_linked_count = records[0]["count"]

        graph_rel_count = graph_rel_has_count + graph_rel_linked_count

        print(
            f"db_relationship_count {db_relationship_count} graph_rel_has_count {graph_rel_has_count} graph_rel_linked_count {graph_rel_linked_count}"
        )

        if db_relationship_count != graph_rel_count:
            _metric(status=2, message="graph sync error")

        _metric(status=0, message="ok")

        db_entity_geo_count = _db_entity_geo_count(db)
        db_entity_location_count = _db_entity_location_count(db)

        print(f"db_entity_geo_count {db_entity_geo_count} db_entity_location_count {db_entity_location_count}")

        if db_entity_geo_count != db_entity_location_count:
            _metric(status=2, message="graph sync error")

    return 0


def _db_entity_count(db) -> int:
    return _db_entity_unique_count(db) + _db_entity_slug_value_count(db)


def _db_entity_geo_count(db: sqlmodel.Session) -> int:
    """count entity objects with lat/lon slugs"""
    query = "slug:lat"
    struct_entities = services.entities.List(db=db, query=query, offset=0, limit=1024).call()

    return struct_entities.count


def _db_entity_location_count(db: sqlmodel.Session) -> int:
    """count entity location objects"""
    struct_count = services.entity_locations.CountIds(db=db).call()
    return struct_count.count


def _db_entity_slug_value_count(db: sqlmodel.Session) -> int:
    """count unique slug, value pairs for entity nodes eq 1"""
    struct_count = services.entities.CountSlugValues(db=db, node=1).call()
    return struct_count.count


def _db_entity_unique_count(db: sqlmodel.Session) -> int:
    """count unique entity objects"""
    struct_count = services.entities.CountIds(db=db).call()
    return struct_count.count


def _db_relationship_count(db: sqlmodel.Session) -> int:
    return _db_relationship_has_count(db) + _db_relationship_linked_count(db)


def _db_relationship_has_count(db: sqlmodel.Session) -> int:
    """ " find entity slugs with node eq 1"""
    query = "node:1"
    struct_entities = services.entities.List(db=db, query=query, offset=0, limit=1024).call()

    return struct_entities.count * 2


def _db_relationship_linked_count(db: sqlmodel.Session) -> int:
    struct_data_links = services.data_links.List(db=db, query="", offset=0, limit=1024).call()

    # find unique name, slug, value tuples with count
    struct_tuples = services.entities.CountNameSlugValues(db=db, node=1).call()

    count = 0

    for data_link in struct_data_links.objects:
        # find src entites for relationships
        src_entities = [t for t in struct_tuples.objects if t.name == data_link.src_name and t.slug == data_link.src_slug]

        for src_object in src_entities:
            # find matching dst entities for each src
            for dst_object in struct_tuples.objects:
                if dst_object.name == data_link.dst_name and dst_object.slug == data_link.dst_slug and dst_object.value == src_object.value:
                    # src_object should be linked to dst_object, and dst_object to src_object
                    count += 1

    return count


def _metric(status: int, message: str):
    pass
