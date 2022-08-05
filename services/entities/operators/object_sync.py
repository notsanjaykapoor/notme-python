import dataclasses

import sqlmodel
import ulid

import services.data_models
import services.entities
import services.kafka.topics


@dataclasses.dataclass
class Struct:
    code: int
    ids: list[int]
    entity_ids: set[str]
    location_ids: list[int]
    errors: list[str]


class ObjectSync:
    """
    sync object to postgres database
    """

    def __init__(self, db: sqlmodel.Session, object: dict):
        self._db = db
        self._object = object

    def call(self) -> Struct:
        struct = Struct(0, [], set(), [], [])

        struct_dms = services.data_models.Hash(db=self._db, query="").call()

        object = self._object_props_validate_id_present(self._object)

        properties = self._object_props_validate_id_slug_present(
            object=object,
            properties=object["properties"],
        )

        if self._object_props_validate_id(object, properties) != 0:
            struct.code = 422
            struct.errors.append("invalid id")
            return struct

        # normalize object into entity objects
        struct_normalize = services.entities.Normalize(
            object=object,
            properties=properties,
            data_models=struct_dms.object,
        ).call()

        entities = struct_normalize.entities

        # resolve entities
        struct_resolve = services.entities.Resolve(
            db=self._db,
            entities=entities,
        ).call()

        if struct_resolve.code not in [200, 201, 409]:
            struct.code = struct_resolve.code
            return struct

        if struct_resolve.code == 409:
            # entity exists
            struct.ids = [entity.id for entity in struct_resolve.entities if entity.id]
            struct.entity_ids = set([entity.entity_id for entity in struct_resolve.entities])
            struct.code = 409

            return struct

        # entity create

        # set entity version and fingerprint
        for entity in entities:
            entity.fingerprint = struct_resolve.fingerprint
            entity.version = struct_resolve.version

        # persist to database with version id
        struct_create = services.entities.Create(self._db, entities=entities).call()

        if struct_create.code == 0:
            struct.code = 201
            struct.ids += struct_create.ids
            struct.entity_ids = struct_create.entity_ids
            struct.location_ids += struct_create.location_ids

        if struct_resolve.code == 200:
            # entity changed, mark original version as replaced
            services.entities.Replace(
                self._db,
                entities=struct_resolve.entities,
            ).call()

            struct.code = 200

        return struct

    def _object_props_validate_id(self, object: dict, properties: list[dict]) -> int:
        """validate object id matches id slug"""
        prop_hash = [prop_hash for prop_hash in properties if prop_hash["slug"] == "id"][0]

        if prop_hash["value"] != object["id"]:
            # invalid id
            return 1

        return 0

    def _object_props_validate_id_present(self, object: dict) -> dict:
        """add object id iff its missing"""

        if "id" in object:
            return object

        # clone and add id property
        object_clone = object.copy()

        object_clone["id"] = ulid.new().str

        return object_clone

    def _object_props_validate_id_slug_present(self, object: dict, properties: list[dict]) -> list[dict]:
        """add id slug iff its missing"""
        slugs = [property["slug"] for property in properties]

        if "id" in slugs:
            return properties

        # clone and add id property
        props_clone = properties.copy()

        props_clone.append(
            {
                "slug": "id",
                "type": "string",
                "value": object["id"],
            }
        )

        return props_clone
