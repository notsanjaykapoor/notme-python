import dataclasses

import sqlmodel
import ulid

import log
import services.entities


@dataclasses.dataclass
class Struct:
    code: int
    entities: list[dict]
    errors: list[str]


PREFIX = "tomtom-"


class MapEntity:
    """map place object to entity objects"""

    def __init__(self, db: sqlmodel.Session, place: dict):
        self._db = db
        self._place = place

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [], [])

        # build and check key
        key = self._key(id=self._place["id"])

        if self._exists(key=key) > 0:
            struct.code = 409
            return struct

        id = ulid.new().str
        name = self._place["poi"]["name"]

        city = self._place["address"]["municipality"].lower()
        lat = self._place["position"]["lat"]
        lon = self._place["position"]["lon"]
        street = self._place["address"]["freeformAddress"].lower()
        postal_code = self._place["address"]["postalCode"]

        struct.entities.append(self._entity(id=id, key=key, name=name, slug="city", value=city))
        struct.entities.append(self._entity(id=id, key=key, name=name, slug="lat", value=str(lat)))
        struct.entities.append(self._entity(id=id, key=key, name=name, slug="lon", value=str(lon)))
        struct.entities.append(self._entity(id=id, key=key, name=name, slug="street", value=street))
        struct.entities.append(self._entity(id=id, key=key, name=name, slug="postal_code", value=postal_code))

        return struct

    def _entity(self, id: str, key: str, name: str, slug: str, value: str) -> dict:
        dict = {
            "entity_id": id,
            "entity_name": "place",
            "entity_key": key,
            "name": name,
            "slug": slug,
            "type_name": "string",
            "type_value": value,
        }

        return dict

    def _exists(self, key: str) -> int:
        struct_list = services.entities.List(
            db=self._db,
            query=f"entity_key:{key}",
            offset=0,
            limit=1,
        ).call()

        if struct_list.count > 0:
            return 1

        return 0

    def _key(self, id: str) -> str:
        """build key from place id str"""
        return f"{PREFIX}{id}"
