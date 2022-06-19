import dataclasses
import logging
import re
import typing

import sqlmodel

import models
import services.entities.watches
import services.mql


@dataclasses.dataclass
class Struct:
    code: int
    watches: list[models.EntityWatch]
    count: int
    errors: list[str]


class Match:
    """find all matching watches for the specified entity list"""

    def __init__(self, db: sqlmodel.Session, entity_ids: typing.Sequence[typing.Union[int, str]], topic: typing.Optional[str] = None):
        self._db = db
        self._entity_ids = entity_ids
        self._topic = topic

        if self._topic:
            self._query = f"topic:{self._topic}"
        else:
            self._query = ""

        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        # get all entity objects
        entities = self._get_all_entities()

        if not entities:
            return struct

        # get watches
        struct_watches = services.entities.watches.List(self._db, self._query, 0, 100).call()

        for watch in struct_watches.objects:
            if self._watch_entities_eval(watch, entities) > 0:
                # watch is not a match
                continue

            struct.watches.append(watch)
            struct.count += 1

        return struct

    def _get_all_entities(self) -> list[models.Entity]:
        entities = []

        for id in self._entity_ids:
            entities += services.entities.get_all_by_id(db=self._db, id=id)

        return entities

    def _watch_entities_eval(self, watch: models.EntityWatch, entities: list[models.Entity]) -> int:
        for entity in entities:
            # find at least one that matches
            if self._watch_entity_eval(watch, entity) == 0:
                return 0

        return 1

    def _watch_entity_eval(self, watch: models.EntityWatch, entity: models.Entity) -> int:
        """check if watch matches entity"""

        struct_tokens = services.mql.Parse(watch.query).call()

        for token in struct_tokens.tokens:
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

            elif re.match(r"\S+\|\S+", value):
                # in match
                values = value.split("|")

                if object_value not in values:
                    return 1
            else:
                # equal match
                if object_value != value:
                    return 1

        return 0
