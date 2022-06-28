import dataclasses
import os

import requests

import log


@dataclasses.dataclass
class Struct:
    code: int
    objects: list[dict]
    count: int
    total: int
    errors: list[str]


class Poi:
    def __init__(self, query: str, lat: float, lon: float, radius: int, offset: int = 0, limit: int = 10):
        self._query = query
        self._lat = lat
        self._lon = lon
        self._radius = radius  # in meters
        self._offset = offset
        self._limit = limit

        self._key = os.environ.get("TOMTOM_API_KEY")
        self._url = f"https://api.tomtom.com/search/2/poiSearch/{self._query}.json"
        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, 0, [])

        params = {
            "key": self._key,
            "lat": self._lat,
            "lon": self._lon,
            "limit": self._limit,
            "ofs": self._offset,
            "radius": self._radius,
        }

        response = requests.get(self._url, params=params)

        struct.objects = response.json()["results"]
        struct.count = len(struct.objects)

        struct.total = response.json()["summary"]["totalResults"]

        return struct
