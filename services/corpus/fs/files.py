import dataclasses
import os
import re

import services.corpus
import services.corpus.fs


@dataclasses.dataclass
class Struct:
    code: int
    files_list: list[str]
    files_map: dict
    errors: list[str]


def files(source_uri: str, filter: str) -> Struct:
    """
    List files in source directory, returns a struct with a list of file names and a mapping of metadata
    """
    struct = Struct(
        code=0,
        files_list=[],
        files_map={},
        errors=[],
    )

    if source_uri.startswith("file://"):
        _, _, local_dir = services.corpus.fs.source_uri_parse(source_uri=source_uri)
    else:
        local_dir = source_uri

    for file in os.listdir(local_dir):
        if file and not re.search(filter, file):
            continue # file excluded by filter

        local_path = f"{local_dir}/{file}"
        stats = os.stat(local_path)

        # exclude directories
        if not os.path.isfile(local_path):
            continue

        struct.files_map[file] = {
            "file_size": stats.st_size,
            "local_dir": local_dir,
            "local_path": local_path,
        }

    struct.files_list = sorted(struct.files_map.keys())

    return struct


def files_path_list(source_uri: str, filter: str) -> Struct:
    """
    List files in source directory, returns a list of file paths
    """

    files_struct = files(source_uri=source_uri, filter=filter)

    return sorted([file_object.get("local_path") for file_object in files_struct.files_map.values()])


