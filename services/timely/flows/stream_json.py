import dataclasses
import os
import sys
import typing

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import bytewax  # # noqa: E402
import bytewax.inputs  # # noqa: E402

import log  # noqa: E402
import models  # noqa: E402

# DATA_MODELS_STATIC = {"name": {"type": "string"}}


@dataclasses.dataclass
class Struct:
    code: int
    output: list[tuple[int, dict]]
    errors: list[str]


class StreamJson:
    """
    timely dataflow to import a json data stream
    """

    def __init__(self, input: typing.Callable, data_mappings: list[models.DataMapping], data_models: list[models.DataModel]):
        self._input = input
        self._data_mappings = data_mappings
        self._data_models = data_models

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [], [])

        data_flow = bytewax.Dataflow()
        data_flow.map(self._map_clean)
        data_flow.map(self._map_normalize)
        data_flow.capture()

        struct.output = bytewax.run(data_flow, self._input)

        return struct

    def _map_clean(self, object: dict) -> dict:
        """
        clean object
          - downcase
          - remove empty keys
        """

        return object

    def _map_normalize(self, object: dict) -> dict:
        """
        normalize json object
          - input: {'model': 'person', 'properties': []}
          - output: {'person.email': {'type': 'string', 'value': 'user@gmail.com'}}
        """

        object_normalized: dict[str, list[dict]] = {}

        model = object["model"]
        props = object["properties"]
        name = object.get("name", None)

        if name:
            # set 'model'.name attribute
            model_field = f"{model}.name"
            object_map = {
                "value": name,
                "type": "string",
            }

            if model_field not in object_normalized:
                object_normalized[model_field] = []

            object_normalized[model_field].append(object_map)

        for prop in props:
            slug = prop["slug"]
            model_field = f"{model}.{slug}"

            object_map = {
                "value": prop["value"],
                "type": prop["type"],
            }

            # check pk - lazy approach
            if (slug in ["_id", "id"]) or ("pk" in prop):
                object_map["pk"] = 1

            if model_field not in object_normalized:
                object_normalized[model_field] = []

            object_normalized[model_field].append(object_map)

        return object_normalized
