import dataclasses
import json
import os
import sys
import typing

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import bytewax  # # noqa: E402
import bytewax.dataflow  # # noqa: E402
import bytewax.execution  # noqa: E402
import bytewax.inputs  # noqa: E402
import bytewax.outputs  # noqa: E402

import log  # noqa: E402
import models  # noqa: E402

DATA_MODELS_STATIC = {"name": {"type": "string"}}


@dataclasses.dataclass
class Struct:
    code: int
    errors: list[str]


class StreamCsv:
    """
    timely dataflow to import a csv data stream
    """

    def __init__(
        self,
        input: bytewax.inputs.InputConfig,
        output: bytewax.outputs.OutputConfig,
        data_mapping: models.DataMapping,
        data_models: list[models.DataModel],
    ):
        self._input = input
        self._output = output
        self._data_mapping = data_mapping
        self._data_models = data_models

        self._obj_mapping = self._data_mapping.obj_mapping
        self._obj_pks_list = self._data_mapping.obj_pks_list
        self._model_name = self._data_mapping.model_name
        self._data_models_by_name_slug = self._build_data_models_by_name_slug()
        self._data_models_static = DATA_MODELS_STATIC

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [])

        data_flow = bytewax.dataflow.Dataflow()
        data_flow.input("input", self._input)
        data_flow.map(self._map_clean)
        data_flow.map(self._map_transform)
        data_flow.map(self._map_derived)
        data_flow.capture(self._output)

        bytewax.execution.run_main(data_flow)

        return struct

    def _build_data_models_by_name_slug(self) -> dict:
        name_slug_dict = {}

        for data_model in self._data_models:
            name_slug = self._build_name_slug(name=data_model.object_name, slug=data_model.object_slug)  # e.g. person.email
            name_slug_dict[name_slug] = data_model

        return name_slug_dict

    def _build_name_slug(self, name: str, slug: str) -> str:
        return f"{name}.{slug}"

    def _map_clean(self, object: dict) -> dict:
        """clean object - downcase, remove empty keys"""

        object_cleaned = {}

        # remove empty keys
        for key in object.keys():
            if key:
                object_cleaned[key.lower()] = object[key]

        return object_cleaned

    def _map_derived(self, object: dict) -> dict:
        """map derived fields based on data_mapping"""
        import services.timely.library.transforms

        object = services.timely.library.transforms.transform_first_last(
            object=object,
            model_name=self._model_name,
            model_slugs=["name"],
        )

        return object

    def _map_transform(self, object: dict) -> dict:
        """map object fields based on data_mapping and data_models to normal form"""
        object_normal = {}

        for key, key_mapped in self._obj_mapping.items():
            # find matching data_model
            name_slug = self._build_name_slug(name=self._model_name, slug=key_mapped)
            data_model = self._data_models_by_name_slug.get(name_slug, None)

            # multi-value keys - normalize key value to a list
            if isinstance(object[key], list):
                key_values = object[key]
            else:
                key_values = [object[key]]

            values = []

            # multi-value keys
            for key_value in key_values:
                value_object = {"value": key_value}

                if not data_model:
                    # check static fields
                    if key_mapped in self._data_models_static.keys():
                        value_object["type"] = self._data_models_static[key_mapped]["type"]
                    else:
                        # data_model field not mapped
                        value_object["type"] = "unmapped"
                else:
                    value_object["type"] = data_model.object_type

                    # check pk field
                    if key in self._obj_pks_list:
                        value_object["pk"] = 1

                values.append(value_object)

            object_normal[name_slug] = values

        return object_normal

    def _output_builder(self, worker_index, worker_count):
        def output_handler(item):
            line = json.dumps(item)
            print(line)
            return line

            # return output_handler
