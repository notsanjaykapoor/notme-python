import dataclasses
import json
import os
import hashlib
import re

import llama_index.core
import llama_index.core.multi_modal_llms.generic_utils
import llama_index.core.node_parser
import llama_index.core.node_parser.text
import llama_index.embeddings.huggingface
import llama_index.readers.file
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

MODEL_NAME_DEFAULT = "gte-large"
SPLITTER_NAME_DEFAULT = "chunk:1024:40"


def files_docs(files: list[str]) -> list:
    """
    Load files into docs.  The returned docs are ready for splitting into nodes.
    """
    docs = []

    partition = files_partition(files=files)

    for type, files in partition.items():
        if type == "dir" and files:
            reader = llama_index.core.SimpleDirectoryReader(input_files=files)
            reader_docs = reader.load_data()
            docs.extend(reader_docs)
        elif type == "pdf" and files:
            reader = llama_index.readers.file.PDFReader()
            for file in files:
                reader_docs = reader.load_data(file)
                docs.extend(reader_docs)

    return docs


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


def files_partition(files: list[str]) -> dict:
    """
    Partition files by type
    """
    file_types = {
        "pdf": [],
        "dir": [],
    }

    for file in files:
        file_type = file.split(".")[-1]

        if file_type in ["pdf"]:
            file_types["pdf"].append(file)
        elif file_type in ["csv", "docx", "epub", "hwp", "ipynb", "jpeg", "jpg", "mbox", "md", "mp3", "mp4", "png", "ppt", "pptm", "pptx"]:
            file_types["dir"].append(file)
        else:
            raise ValueError(f"unsupported file {file}")

    return file_types


def file_uri_parse(source_uri: str) -> tuple[str, str, str]:
    """
    """
    if not (match := re.match(r'^file:\/\/([^\/]+)\/(.+)$', source_uri)):
        raise ValueError(f"invalid source_uri {source_uri}")

    source_host, source_path = (match[1], match[2])

    match = re.match(r'^(.+)\/(.+)$$', source_path)
    source_dir = match[1]

    return source_host, source_dir, source_path


def model_dims(model: str) -> int:
    """
    return model dimensions from config.json
    """
    models_root = os.environ["APP_MODELS_PATH"]
    models_path = f"{models_root}/{model}"

    if not os.path.exists(models_path):
        raise ValueError(f"model not found {models_path}")

    config_json = json.load(open(f"{models_path}/config.json"))

    if "hidden_size" in config_json.keys():
        return config_json.get("hidden_size")

    return DIMENSIONS[model]


def model_klass(model: str, device: str) -> llama_index.embeddings.huggingface.HuggingFaceEmbedding:
    """
    return huggingface embedding model object
    """
    models_root = os.environ["APP_MODELS_PATH"]
    models_path = f"{models_root}/{model}"

    if not os.path.exists(models_path):
        raise ValueError(f"model not found {models_path}")

    embeddings = llama_index.embeddings.huggingface.HuggingFaceEmbedding(
        device=device,
        model_name=models_path,
        trust_remote_code=True,
    )

    return embeddings


def model_names() -> list[str]:
    models_root = os.environ["APP_MODELS_PATH"]
    return os.listdir(models_root)


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


def text_splitter(name: str, model_klass) -> llama_index.core.node_parser.text:
    """
    Map splitter name to text splitter class
    """
    if name == "semantic":
        text_splitter = llama_index.core.node_parser.SemanticSplitterNodeParser(
            buffer_size=1, breakpoint_percentile_threshold=95, embed_model=model_klass
        )
    elif name.startswith("chunk"):
        _, chunk_size, chunk_overlap = name.split(":")
        text_splitter = llama_index.core.node_parser.SentenceSplitter(
            chunk_size=int(chunk_size),
            chunk_overlap=int(chunk_overlap),
        )
    else:
        raise ValueError(f"invalid splitter {name}")

    return text_splitter


def torch_device() -> str:
    """
    return supported pytorch device on this machine, should be one of 'cpu', 'mps', 'cuda'
    """
    if torch.cuda.is_available():
        return "cuda"

    if torch.backends.mps.is_available():
        return "mps"

    return "cpu"