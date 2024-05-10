import dataclasses

import langchain.text_splitter
import langchain_community.document_loaders
import langchain_community.embeddings
import langchain_community.vectorstores
import langchain_openai
import langchain_postgres.vectorstores
import  services.corpus

@dataclasses.dataclass
class Struct:
    code: int
    docs: list
    errors: list[str]


def retrieve(db_url: str, db_name: str, retriever_type: str, query: str) -> Struct:
    """
    """
    struct = Struct(0, [], [])

    parse_result = services.corpus.name_parse(database=db_name)
    model = parse_result.model

    if model == "gpt4all":
        embeddings = langchain_community.embeddings.GPT4AllEmbeddings()
    elif model == "openai":
        embeddings = langchain_openai.OpenAIEmbeddings()
    else:
        embeddings = langchain_community.embeddings.HuggingFaceHubEmbeddings(model=model)

    db = langchain_postgres.vectorstores.PGVector(
        embeddings=embeddings,
        collection_name=db_name,
        connection=f"{db_url}/{db_name}",
        use_jsonb=True,
    )
    db_retriever = db.as_retriever()

    if retriever_type == "compress":
        embeddings_filter = langchain.retrievers.document_compressors.EmbeddingsFilter(embeddings=embeddings, similarity_threshold=0.76)
        compression_retriever = langchain.retrievers.ContextualCompressionRetriever(
            base_compressor=embeddings_filter, base_retriever=db_retriever
        )

        struct.docs = compression_retriever.invoke(query)
    else:
        struct.docs = db_retriever.invoke(query)

    return struct
