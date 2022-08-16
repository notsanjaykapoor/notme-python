import dataclasses

import sqlmodel
import ulid

import services.data_models
import services.entities
import services.kafka.topics


@dataclasses.dataclass
class Struct:
    code: int
    id: str
    errors: list[str]


class IdResolve:
    """
    timely operator to map id to an existing entity object, otherwise return a new id
    """

    def __init__(self, db: sqlmodel.Session, object: dict):
        self._db = db
        self._object = object

    def call(self) -> Struct:
        struct = Struct(0, "", [])

        # find fields that are marked as pk, note that this can be a composite field
        entity_pks = [key for key in self._object.keys() if self._object[key].get("pk", 0) == 1]

        entity_klass, _ = entity_pks[0].split(".")
        entity_query = [f"entity_name:{entity_klass}"]

        for entity_pk in entity_pks:
            _, entity_slug = entity_pk.split(".")
            entity_value = self._object[entity_pk]["value"]

            entity_query.append(f"slug:{entity_slug}")
            entity_query.append(f"type_value:{entity_value}")

        struct_entities = services.entities.List(
            db=self._db,
            query=" ".join(entity_query),
            offset=0,
            limit=1,
        ).call()

        if len(struct_entities.objects):
            # entity exists
            entity = struct_entities.objects[0]

            struct.id = entity.entity_id
            struct.code = 200

            return struct

        struct.id = ulid.new().str
        struct.code = 201

        return struct
