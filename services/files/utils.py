import hashlib
import os
import re


def file_uri_parse(source_uri: str) -> tuple[str, str, str]:
    """
    """
    if not (match := re.match(r'^file:\/\/([^\/]+)\/(.+)$', source_uri)):
        raise ValueError(f"invalid source_uri {source_uri}")

    source_host, source_path = (match[1], match[2])

    match = re.match(r'^(.+)\/(.+)$$', source_path)
    source_dir = match[1]

    return source_host, source_dir, source_path


def files_fingerprint(files: list[str]) -> str:
    """
    Generate md5 fingerprint using file metadata
    """
    files_list = []

    for file in sorted(files):
        file_stats = os.stat(file)
        size_bytes = file_stats.st_size
        files_list.append(f"{file.lower()}:{size_bytes}")

    files_str = ",".join(files_list)

    return hashlib.md5(files_str.encode("utf-8")).hexdigest()
