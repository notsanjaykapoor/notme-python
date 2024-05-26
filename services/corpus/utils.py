import dataclasses
import os
import hashlib
import re

import llama_index.embeddings.huggingface

@dataclasses.dataclass
class Struct:
    code: int
    corpus: str
    encoded: str
    model: str
    errors: list[str]


DIMENSIONS = {
    "bge-large-en-v1-5-finetuned-300": 1024,
    "clip-vit-base-patch32": 512,
    "gte-base": 768,
    "gte-large": 1024,
    "nomic-embed-text-v1": 768,
}

MODEL_NAME_DEFAULT = "gte-large"
SPLITTER_NAME_DEFAULT = "chunk:1024:40"


def embed_dims(model: str) -> int:
    return DIMENSIONS[model]


def embed_model(model: str) -> llama_index.embeddings.huggingface.HuggingFaceEmbedding:
    models_root = os.environ["HF_MODELS_PATH"]
    models_path = f"{models_root}/{model}"

    if not os.path.exists(models_path):
        raise ValueError(f"invalid model {model}")

    embeddings = llama_index.embeddings.huggingface.HuggingFaceEmbedding(
        model_name=models_path,
        trust_remote_code=True,
    )

    return embeddings


def embed_models() -> list[str]:
    models_root = os.environ["HF_MODELS_PATH"]
    return os.listdir(models_root)


def files_fingerprint(files: list[str]) -> str:
    """
    Generate md5 fingerprint for fileset
    """
    files_list = []

    for file in sorted(files):
        file_stats = os.stat(file)
        size_bytes = file_stats.st_size
        files_list.append(f"{file.lower()}:{size_bytes}")

    files_str = ",".join(files_list)

    return hashlib.md5(files_str.encode("utf-8")).hexdigest()


def name_encode(corpus: str, model: str, splitter: str) -> str:
    """
    """
    corpus_normalized = re.sub(r'[-:\s]+', "_", corpus.lower())
    model_normalized = re.sub(r'[-:\s]+', "_", model.lower())
    splitter_normalized = re.sub(r'[-:\s]+', "_", splitter.lower())

    name_encoded = f"c_{corpus_normalized}_m_{model_normalized}_s_{splitter_normalized}"

    return name_encoded


def source_uri_parse(source_uri: str) -> tuple[str, str, str, str]:
    """
    """
    if not (match := re.match(r'^file:\/\/([^\/]+)\/(.+)$', source_uri)):
        raise ValueError(f"invalid source_uri {source_uri}")

    source_host, source_path = (match[1], match[2])

    if source_host == "localhost":
        # check if file/dir exists
        if not os.path.exists(source_path):
            raise ValueError(f"invalid path {source_path}")

        source_name = re.sub(r'[\.\/]+', "_", source_path).strip("_")
    else:
        raise ValueError(f"invalid host {source_host}")

    return source_name, source_host, source_path