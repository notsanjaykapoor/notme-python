import dataclasses
import os
import re


def trigger_ingest_events(dirs: list[str]) -> Struct:
    """
    List all corpus collections
    """

    for dir in dirs:
        files = os.listdir(dir)
