import dataclasses
import logging
import re
import sys

import sqlalchemy
import sqlmodel

import models
import services.entities.watches
import services.mql


@dataclasses.dataclass
class Struct:
    code: int
    ids: list[int]
    count: int
    errors: list[str]


class Create:
    def __init__(self, db: sqlmodel.Session, entity: models.Entity):
        self._db = db
        self._entity = entity

        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        # get watches
        struct_watches = services.entities.watches.List(self._db, "", 0, 100).call()

        for watch in struct_watches.objects:
            if self._watch_eval(watch) > 0:
                # watch is not a match
                continue

            try:
                # found a match, create db object
                db_object = models.EntityMatch(
                    entity_id=self._entity.entity_id,
                    watch_id=watch.id,
                )

                self._db.add(db_object)
                self._db.commit()

                if db_object.id:
                    struct.ids.append(db_object.id)
                    struct.count += 1
            except sqlalchemy.exc.IntegrityError:
                self._db.rollback()
                struct.code = 409
                self._logger.error(f"{__name__} {sys.exc_info()[0]} error")
            except Exception:
                self._db.rollback()
                struct.code = 500
                self._logger.error(f"{__name__} {sys.exc_info()[0]} exception")

        return struct

    def _watch_eval(self, watch: models.EntityWatch) -> int:
        """check if watch matches entity"""

        struct_tokens = services.mql.Parse(watch.query).call()

        for token in struct_tokens.tokens:
            field = token["field"]
            value = token["value"]

            # check if watch query field matches
            object_value = self._entity.__dict__[field]

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
