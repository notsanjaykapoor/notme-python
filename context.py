import contextvars

import ulid

request_id: contextvars.ContextVar = contextvars.ContextVar("request_id", default=ulid.new().str)


def rid_set(id: str) -> int:
    request_id.set(id)
    return 0


def rid_get() -> str:
    return request_id.get()
