import dataclasses

import langchain.text_splitter
import langchain_community.document_loaders
import langchain_community.embeddings
import langchain_community.vectorstores
import langchain_postgres.vectorstores
import sqlalchemy
import sqlalchemy_utils.functions

@dataclasses.dataclass
class Struct:
    code: int
    chunks_count: int
    docs_count: int
    errors: list[str]


def write(db_url: str, db_name: str, embeddings: langchain_community.embeddings, config: dict) -> Struct:
    """
    Load documents, split them into chunks and store embeddings in a local vector store.
    """

    _create_db(db_url=db_url, db_name=db_name)

    if "dir" in config.keys():
        return _write_dir(db_name=db_name, embeddings=embeddings, dir=config.get("dir"))

    if "urls" in config.keys():
        return _write_urls(db_name=db_name, embeddings=embeddings, urls=config.get("urls"))

    raise ValueError("invalid config")


def _create_db(db_url:str, db_name: str) -> int:
    """
    Create corpus database

    Note that postgres does not allow 'create database' to be run inside a transaction.
    """
    db_name_url = f"{db_url}/{db_name}"
    engine = sqlalchemy.create_engine(db_name_url, echo=False)

    if not sqlalchemy_utils.functions.database_exists(engine.url):
        sqlalchemy_utils.functions.create_database(engine.url)

    return 0

def _write_dir(db_name: str, embeddings: langchain_community.embeddings, dir: str) -> Struct:
    """
    """        
    struct = Struct(0, 0, 0, [])

    loader = langchain_community.document_loaders.DirectoryLoader(dir)
    documents = loader.load()

    text_splitter = langchain.text_splitter.CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    db = langchain_postgres.vectorstores.PGVector.from_documents(
        embedding=embeddings,
        documents=texts,
        collection_name=db_name,
        connection=f"postgresql+psycopg://postgres:development@pgvector-dev:5435/{db_name}",
        pre_delete_collection=True,
        use_jsonb=True,
    )

    # db = langchain_community.vectorstores.FAISS.from_documents(texts, embedding=embeddings)
    # db.save_local(db_name)

    # struct.chunks_count = db.index.ntotal
    struct.docs_count = len(documents)

    return struct


def _write_urls(db_name: str, embeddings: langchain_community.embeddings, urls: list[str]) -> Struct:
    """
    """
    struct = Struct(0, 0, 0, [])

    loader = langchain_community.document_loaders.UnstructuredURLLoader(urls)
    documents = loader.load()

    text_splitter = langchain.text_splitter.CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    # text_splitter = langchain.text_splitter.CharacterTextSplitter(chunk_size=400, chunk_overlap=20)
    texts = text_splitter.split_documents(documents)

    db = langchain_community.vectorstores.FAISS.from_documents(texts, embedding=embeddings)
    db.save_local(db_name)

    # struct.chunks_count = db.index.ntotal
    struct.docs_count = len(documents)

    return struct
