import services.corpus.fs


def detect(files: list[str]) -> str:
    """
    detect model name based on file types
    """
    files_result = services.corpus.fs.files_partition(files=files)

    if files_result.reader_img:
        if files_result.reader_dir or files_result.reader_pdf:
            # clip supports both images and text, but lets support that later
            raise ValueError("multimodal corpus not suported yet")
        return "clip:default"
    
    return "local:gte-large"



