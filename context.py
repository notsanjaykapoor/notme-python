import contextvars
import ulid

# note: look into how these operate with async tasks
request_id = contextvars.ContextVar("request_id", default=ulid.new().str)
