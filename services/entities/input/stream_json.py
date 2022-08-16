import json
import typing


def stream_json(file: str) -> typing.Generator[tuple[int, dict], None, None]:
    objects = json.load(open(file))

    for object in objects:
        yield 1, object
