import os
import shutil

import services.corpus

def delete_by_name(dir: str) -> int:
    """
    Delete faiss collection
    """
    if dir.startswith("file://"):
        _, _, local_dir = services.corpus.source_uri_parse(source_uri=dir)
    else:
        local_dir = dir

    if not os.path.isdir(local_dir):
        return 404

    shutil.rmtree(local_dir)

    return 0
