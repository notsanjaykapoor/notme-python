import os

TOPIC_GEOFENCE_ALERTS = "geofence-alerts"
TOPIC_GRAPH_SYNC = "graph-sync"

TOPIC_UP = "up"


def topic_up() -> str:
    return f"{TOPIC_UP}-{os.environ['APP_ENV']}"
