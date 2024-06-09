import dataclasses
import re

import torch

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
}


def name_encode(corpus: str, prefix: str, model: str, splitter: str) -> str:
    """
    Encode corpus name with the following constraints:
      - lowercase, underscore only
      - uses corpus, model, and splitter as part of the name
      - somewhat human readable
      - ensure name starts with prefix, if specified
    """
    corpus_normalized = re.sub(r'[-:\s]+', "_", corpus.lower())
    model_normalized = re.sub(r'[-:\s]+', "_", model.lower())
    splitter_normalized = re.sub(r'[-:\s]+', "_", splitter.lower())

    if prefix:
        if not (match := re.match(rf"(.*)({prefix})(.*)", corpus_normalized)):
            raise ValueError(f"invalid corpus name {corpus}")

        corpus_normalized = f"{match[2]}{match[3]}"

    name_encoded = f"c_{corpus_normalized}_m_{model_normalized}_s_{splitter_normalized}"

    return name_encoded


def name_generate(corpus: str, strip: str) -> str:
    """
    Encode corpus name with the following constraints:
      - lowercase, underscore only
      - name based on corpus
      - somewhat human readable
      - ensure name is stripped with 'strip', if specified
    """
    corpus_normalized = re.sub(r'[-:\s]+', "_", corpus.lower())

    if strip:
        corpus_normalized = corpus_normalized.strip(strip)
        # if not (match := re.match(rf"(.*)({prefix})(.*)", corpus_normalized)):
        #     raise ValueError(f"invalid corpus name {corpus}")
        # corpus_normalized = f"{match[2]}{match[3]}"

    return corpus_normalized


def torch_device() -> str:
    """
    return supported pytorch device on this machine, should be one of 'cpu', 'mps', 'cuda'
    """
    if torch.cuda.is_available():
        return "cuda"

    if torch.backends.mps.is_available():
        return "mps"

    return "cpu"