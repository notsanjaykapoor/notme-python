import typing

import datadog

from .types import GraphQuery


@datadog.statsd.timed("neo.reader", tags=[f"reader:{__name__}"])
def match_geo_all_from_node(src_label: str, src_id: str, meters: float) -> GraphQuery:
    struct = GraphQuery("", {})

    struct.query = (
        f"match (a:{src_label} {{id: $id}}), (b)"  # noqa: F541
        + f" where point.distance(a.location, b.location) < {meters} and b.id <> a.id"
        + " return b as node, point.distance(a.location, b.location) as distance"
    )

    struct.params = {
        "id": src_id,
    }

    return struct


@datadog.statsd.timed("neo.reader", tags=[f"reader:{__name__}"])
def match_geo_all_from_point(lat: float, lon: float, meters: float) -> GraphQuery:
    struct = GraphQuery("", {})

    struct.query = (
        f"with point({{longitude: $lon, latitude: $lat}}) as p1 match (p2)"  # noqa: F541
        + f" where point.distance(p1, p2.location) < {meters}"
        + " return p2 as node, point.distance(p1, p2.location) as distance"
    )

    struct.params = {
        "lat": lat,
        "lon": lon,
    }

    return struct


@datadog.statsd.timed("neo.reader", tags=[f"reader:{__name__}"])
def match_geo_filtered_from_point(lat: float, lon: float, meters: float, dst_label: typing.Optional[str], dst_id: str) -> GraphQuery:
    struct = GraphQuery("", {})

    if dst_label:
        struct.query = (
            f"with point({{longitude: $lon, latitude: $lat}}) as p1 match (p2:{dst_label} {{id: $dst_id}})"
            + f" where point.distance(p1, p2.location) < {meters}"
            + " return p2.id, p2.location, point.distance(p1, p2.location)"
        )
    else:
        struct.query = (
            f"with point({{longitude: $lon, latitude: $lat}}) as p1 match (p2 {{id: $dst_id}})"  # noqa: F541
            + f" where point.distance(p1, p2.location) < {meters}"
            + " return p2 as node, point.distance(p1, p2.location) as distance"
        )

    struct.params = {
        "lat": lat,
        "lon": lon,
        "dst_id": dst_id,
    }

    return struct
