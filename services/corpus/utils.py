import dataclasses
import os
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


def name_encode(corpus: str, model: str) -> str:
    """
    """
    corpus_normalized = re.sub(r'[-:\s]+', "_", corpus.lower())
    model_normalized = re.sub(r'[-:\s]+', "_", model.lower())

    name_encoded = f"c_{corpus_normalized}_m_{model_normalized}"

    return name_encoded


def name_parse(name_encoded: str) -> Struct:
    """
    """
    struct = Struct(0, "", name_encoded, "", [])

    match = re.search("^c_([^:]+)_m_([^:]+)$", name_encoded)

    if not match:
        struct.code = 422
        return struct

    struct.corpus = match[1]
    struct.model = re.sub("_", "-", match[2])

    return struct
