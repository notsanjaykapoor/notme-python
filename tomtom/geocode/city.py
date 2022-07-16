import dataclasses
import os

import requests  # type: ignore

import log


@dataclasses.dataclass
class Struct:
    code: int
    objects: list[dict]
    count: int
    total: int
    errors: list[str]


class City:
    def __init__(self, name: str):
        self._name = name  # e.g 'chicago', 'chicago il usa'

        self._key = os.environ.get("TOMTOM_API_KEY")
        self._url = f"https://api.tomtom.com/search/2/geocode/{self._name}.json"
        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, 0, [])

        params = {
            "key": self._key,
        }

        response = requests.get(self._url, params=params)

        struct.objects = response.json()["results"]
        struct.count = len(struct.objects)

        struct.total = response.json()["summary"]["totalResults"]

        return struct
