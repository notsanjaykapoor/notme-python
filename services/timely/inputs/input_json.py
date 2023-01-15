import contextvars
import json
import typing

_input_json: contextvars.ContextVar = contextvars.ContextVar("input_json", default="")


def input_json_generator(worker_index: int, workers_count: int, resume_state: str) -> typing.Generator[tuple[int, dict], None, None]:
    file = _input_json.get()

    objects = json.load(open(file))

    for object in objects:
        yield 1, object


def input_json_params(file: str) -> int:
    _input_json.set(file)
    return 0
