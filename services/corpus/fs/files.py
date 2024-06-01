import dataclasses
import os

import sqlmodel

import services.corpus


@dataclasses.dataclass
class Struct:
    code: int
    files_list: list[str]
    files_map: dict
    errors: list[str]


def files(source_uri: str) -> Struct:
    """
    List files in local directory
    """
    struct = Struct(
        code=0,
        files_list=[],
        files_map={},
        errors=[],
    )

    if source_uri.startswith("file://"):
        _, _, local_dir = services.corpus.source_uri_parse(source_uri=source_uri)
    else:
        local_dir = source_uri

    for file in os.listdir(local_dir):
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
