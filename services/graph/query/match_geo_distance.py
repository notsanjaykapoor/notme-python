import dataclasses
import typing


@dataclasses.dataclass
class GraphQuery:
    query: str
    params: dict


def match_geo_distance_from_point(lat: float, lon: float, dst_label: typing.Optional[str], dst_id: str, meters: float) -> GraphQuery:
    struct = GraphQuery("", {})

    if dst_label:
        struct.query = (
            f"with point({{longitude: $lon, latitude: $lat}}) as p1 match (b:{dst_label} {{id: $dst_id}})"
            + f" where point.distance(p1, b.location) < {meters}"
            + " return b.id, b.location, point.distance(p1, b.location)"
        )
    else:
        struct.query = (
            f"with point({{longitude: $lon, latitude: $lat}}) as p1 match (b {{id: $dst_id}})"  # noqa: F541
            + f" where point.distance(p1, b.location) < {meters}"
            + " return b.id, b.location, point.distance(p1, b.location)"
        )

    struct.params = {
        "lat": lat,
        "lon": lon,
        "dst_id": dst_id,
    }

    return struct


def match_geo_distance_from_node(src_label: str, src_id: str, meters: float) -> GraphQuery:
    struct = GraphQuery("", {})

    struct.query = (
        f"match (a:{src_label} {{id: $id}}), (b)"
        + f" where point.distance(a.location, b.location) < {meters} and b.id <> a.id"
        + " return b.id, b.location, point.distance(a.location, b.location)"
    )

    struct.params = {
        "id": src_id,
    }

    return struct
