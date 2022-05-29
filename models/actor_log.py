import json
import logging


class ActorLog:
    def __init__(self, app_name: str):
        self._app_name = app_name

        self._file_name = f"logs/{self._app_name}-log.json"

    def append(self, message: dict) -> int:
        # append to log file
        with open(self._file_name, "a") as f:
            f.write(json.dumps(message))
            f.write("\n")

        return 0
