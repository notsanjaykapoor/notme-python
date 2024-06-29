import wget

import services.files


def download(uri: str, dir: str) -> str:
    """
    download uri to folder
    """
    if uri.startswith("file://"):
        _, _, local_path = services.files.file_uri_parse(source_uri=uri)
        return local_path

    file_path = wget.download(uri, out=dir)

    return file_path


def download_gc( dir: str) -> str:
    """
    delete files from download directory
    """
    
