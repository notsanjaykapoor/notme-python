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

        entity_pk_keys = self._entity_pk_keys()

        if len(entity_pk_keys) > 1:
            # todo: support compose keys
            struct.code = 422
            return struct

        entity_pk_key = entity_pk_keys[0]

        if len(self._object[entity_pk_key]) > 1:
            # error, can't have multiple values for primary key
            struct.code = 422
            return struct

        entity_klass, entity_slug = entity_pk_key.split(".")
        entity_query = [f"entity_name:{entity_klass}", f"slug:{entity_slug}"]

        for entity_pk in self._object[entity_pk_key]:
            entity_value = entity_pk["value"]

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

    def _entity_pk_keys(self) -> list[str]:
        """
        return list of keys that make up the entity pk, note that this can be multiple in the case of a composite key
        """
        keys = []

        for key, object_list in self._object.items():
            if any(object_dict.get("pk", 0) == 1 for object_dict in object_list):
                keys.append(key)

        return keys
