import contextvars

import ulid

# note: look into how these operate with async tasks
request_id = contextvars.ContextVar("request_id", default=ulid.new().str)


def rid_set(id: str) -> int:
    request_id.set(id)
    return 0


def rid_get() -> str:
    return request_id.get()
