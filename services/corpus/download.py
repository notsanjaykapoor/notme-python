import os

import services.corpus


def download(source_uri: str) -> tuple[str, list[str]]:
    """
    """
    _, source_host, source_path = services.corpus.source_uri_parse(source_uri=source_uri)

    if source_host == "localhost":
        # files are in local fs
        local_files = sorted([f"{source_path}/{file}" for file in os.listdir(source_path) if os.path.isfile(f"{source_path}/{file}")])
    else:
        raise ValueError(f"invalid host {source_host}")

    return source_path, local_files