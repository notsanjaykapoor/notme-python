import json
import typing


def input_json(file: str) -> typing.Generator[tuple[int, dict], None, None]:
    objects = json.load(open(file))

    for object in objects:
        yield 1, object
