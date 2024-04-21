import dataclasses

import langchain.text_splitter
import langchain_community.document_loaders
import langchain_community.embeddings
import langchain_community.vectorstores

@dataclasses.dataclass
class Struct:
    code: int
    chunks_count: int
    docs_count: int
    errors: list[str]


def write(db_name: str, embedding: langchain_community.embeddings, config: dict) -> Struct:
    """
    Load documents, split them into chunks and store embeddings in a local vector store.
    """
    if "dir" in config.keys():
        return _write_dir(db_name=db_name, embedding=embedding, dir=config.get("dir"))

    if "urls" in config.keys():
        return _write_urls(db_name=db_name, embedding=embedding, urls=config.get("urls"))

    raise ValueError("invalid config")

def _write_dir(db_name: str, embedding: langchain_community.embeddings, dir: str) -> Struct:
    """
    """        
    struct = Struct(0, 0, 0, [])

    loader = langchain_community.document_loaders.DirectoryLoader(dir)
    documents = loader.load()

    text_splitter = langchain.text_splitter.CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    db = langchain_community.vectorstores.FAISS.from_documents(texts, embedding=embedding)
    db.save_local(db_name)

    struct.chunks_count = db.index.ntotal
    struct.docs_count = len(documents)

    return struct


def _write_urls(db_name: str, embedding: langchain_community.embeddings, urls: list[str]) -> Struct:
    """
    """
    struct = Struct(0, 0, 0, [])

    loader = langchain_community.document_loaders.UnstructuredURLLoader(urls)
    documents = loader.load()

    text_splitter = langchain.text_splitter.CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    db = langchain_community.vectorstores.FAISS.from_documents(texts, embedding=embedding)
    db.save_local(db_name)

    struct.chunks_count = db.index.ntotal
    struct.docs_count = len(documents)

    return struct
