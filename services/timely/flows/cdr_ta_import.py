import dataclasses
import os
import re
import sys
import typing

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import bytewax  # # noqa: E402
import bytewax.inputs  # # noqa: E402

import log  # noqa: E402


@dataclasses.dataclass
class Struct:
    code: int
    errors: list[str]


class CdrTaImport:
    """
    timely dataflow to import timing cdr timing advance data
    """

    def __init__(self, input: typing.Callable):
        self._input = input

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [])

        flow_1 = bytewax.Dataflow()
        flow_1.map(self._map_filter)
        flow_1.capture()

        for epoch, item in bytewax.run(flow_1, self._input):
            self._logger.info(f"flow epoch {epoch} item {item}")

        return struct

    def _map_filter(self, object: dict) -> dict:
        object_mapped = {}

        for key in object:
            key_lower = key.lower()
            if re.search(r"confidence|datetime|duration|latitude|longitude|imei|imsi", key_lower):
                object_mapped[key_lower] = object[key]

        return object_mapped
