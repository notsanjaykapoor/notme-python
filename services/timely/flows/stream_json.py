import dataclasses
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import bytewax  # # noqa: E402
import bytewax.inputs  # # noqa: E402

import models  # noqa: E402


@dataclasses.dataclass
class Struct:
    code: int
    errors: list[str]


def stream_json(
    input: bytewax.inputs.InputConfig,
    output: bytewax.outputs.OutputConfig,
    data_mappings: list[models.DataMapping],
    data_models: list[models.DataModel],
) -> Struct:
    struct = Struct(0, [])

    data_flow = bytewax.dataflow.Dataflow()
    data_flow.input("input", input)
    data_flow.map(_map_clean)
    data_flow.map(_map_normalize)
    data_flow.capture(output)

    bytewax.execution.run_main(data_flow)

    return struct


def _map_clean(object: dict) -> dict:
    """
    clean object
        - downcase
        - remove empty keys
    """

    return object


def _map_normalize(object: dict) -> dict:
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
