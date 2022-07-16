import dataclasses
import re
import typing

import datadog
import neo4j
import sqlmodel

import log
import models
import services.entity_watches
import services.graph.distance
import services.graph.query
import services.graph.session
import services.graph.tx
import services.mql


@dataclasses.dataclass
class Struct:
    code: int
    watches: list[models.EntityWatch]
    count: int
    errors: list[str]


class Match:
    """find all matching watches for the specified entity set"""

    def __init__(
        self,
        db: sqlmodel.Session,
        neo: neo4j.Session,
        entity_ids: typing.Sequence[int | str],
        topic: typing.Optional[str] = None,
    ):
        self._db = db
        self._neo = neo
        self._entity_ids = entity_ids
        self._topic = topic

        if self._topic:
            self._query = f"topic:{self._topic}"
        else:
            self._query = ""

        self._tokens_geo = ["geo", "geofence"]
        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        # get all entity objects
        entities = self._get_all_entities()

        if not entities:
            return struct

        # get watches
        struct_watches = services.entity_watches.List(self._db, self._query, 0, 100).call()

        for watch in struct_watches.objects:
            if self._watch_entities_matches(watch, entities) != 0:
                # watch does not match
                continue

            struct.watches.append(watch)
            struct.count += 1

        return struct

    def _get_all_entities(self) -> list[models.Entity]:
        entities = []

        for id in self._entity_ids:
            entities += services.entities.get_all_by_id(db=self._db, id=id)

        return entities

    def _tokens_partition(self, tokens: list[dict]) -> dict:
        hash: dict = {
            "geo": [],
            "normal": [],
        }

        for token in tokens:
            if token["field"] in self._tokens_geo:
                hash["geo"].append(token)
            else:
                hash["normal"].append(token)

        return hash

    def _watch_entities_matches(self, watch: models.EntityWatch, entities: list[models.Entity]) -> int:
        """returns 0 if watch matches entity; 1 otherwise"""

        # parse query tokens into normal and geo

        struct_tokens = services.mql.Parse(watch.query).call()

        tokens_hash = self._tokens_partition(tokens=struct_tokens.tokens)

        matches = 0

        for entity in entities:
            if self._watch_entity_normal_match(watch, entity, tokens_hash["normal"]) == 0:
                matches += 1

        if not tokens_hash["geo"]:
            # no geo tokens, match success
            return 0 if matches > 0 else 1

        if self._watch_entity_geo_match(watch, entities[0], tokens_hash["geo"]) > 0:
            # geo match failed
            return -1

        return 0

    def _watch_entity_geo_match(self, watch: models.EntityWatch, entity: models.Entity, tokens: list[dict]) -> int:
        """returns 0 if watch matches entity; 1 otherwise"""

        for token in tokens:
            field = token["field"]
            value = token["value"]

            if field == "geofence":
                lat, lon, radius = value.split(",")

                meters = services.graph.distance.meters(radius)

                struct_graph = services.graph.query.match_geo_filtered_from_point(
                    lat=float(lat),
                    lon=float(lon),
                    meters=meters,
                    dst_id=entity.entity_id,
                    dst_label=None,
                )

                records = self._watch_entity_geo_query(query=struct_graph.query, params=struct_graph.params)

                if not records:
                    return 1

        return 0

    def _watch_entity_geo_query(self, query: str, params: dict) -> list[neo4j.Record]:
        with datadog.statsd.timed(f"{__name__}.timer", tags=["env:dev", "neo:read"]):
            records = self._neo.read_transaction(services.graph.tx.read, query, params)

            return records

    def _watch_entity_normal_match(self, watch: models.EntityWatch, entity: models.Entity, tokens: list[dict]) -> int:
        """returns 0 if watch matches entity; 1 otherwise"""

        for token in tokens:
            field = token["field"]
            value = token["value"]

            # check if watch query field matches
            object_value = entity.__dict__.get(field, None)

            if not object_value:
                return 1

            # check if watch query value matches
            if re.match(r"^~", value):
                # regex match
                value_normal = re.sub(r"~", "", value)

                if not (re.match(rf"{value_normal}", object_value)):
                    return 1
            elif re.match(r"\S+\|\S+", value):  # or version 1
                # in match
                values = value.split("|")

                if object_value not in values:
                    return 1
            elif re.match(r"\S+\,\S+", value):  # or version 2
                # in match
                values = value.split(",")

                if object_value not in values:
                    return 1
            else:
                # equal match
                if object_value != value:
                    return 1

        return 0
