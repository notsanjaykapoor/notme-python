import dataclasses
import hashlib
import os
import re

@dataclasses.dataclass
class Struct:
    files_total: int
    reader_dir: list[str]
    reader_idx: list[str]
    reader_img: list[str]
    reader_pdf: list[str]


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


def files_partition(files: list[str]) -> Struct:
    """
    Partition files by type
    """
    struct = Struct(
        files_total=0,
        reader_dir=[],
        reader_idx=[],
        reader_img=[],
        reader_pdf=[],
    )

    for file in files:
        if file.startswith("\."):
            continue # ignore dot files

        struct.files_total += 1

        file_type = file.split(".")[-1]

        if file_type in ["pdf"]:
            struct.reader_pdf.append(file)
        elif file_type in ["csv", "docx", "epub", "hwp", "ipynb", "jpeg", "jpg", "mbox", "md", "mp3", "mp4", "png", "ppt", "pptm", "pptx", "txt"]:
            # check if file is an index file - a file that contains an index pointing to other txt or img files
            if file_type in ["csv"] and "index.csv" in file:
                struct.reader_idx.append(file)
            else:
                if file_type in ["jpeg", "jpg", "png"]:
                    struct.reader_img.append(file)
                else:
                    struct.reader_dir.append(file)
        else:
            raise ValueError(f"unsupported file {file}")

    return struct


def source_uri_parse(source_uri: str) -> tuple[str, str, str]:
    """
    """
    source_host, _source_dir, source_path = file_uri_parse(source_uri=source_uri)

    if source_host == "localhost":
        # check if file/dir exists
        if not os.path.exists(source_path):
            raise ValueError(f"invalid path {source_path}")

        source_name = re.sub(r'[\.\/]+', "_", source_path).strip("_")
    else:
        raise ValueError(f"invalid host {source_host}")

    return source_name, source_host, source_path
