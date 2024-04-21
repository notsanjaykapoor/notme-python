import dataclasses

import langchain.chains
import langchain_community.vectorstores
import langchain_openai.chat_models

@dataclasses.dataclass
class Struct:
    code: int
    chain: langchain.chains
    errors: list[str]


def qa_chain(db: langchain_community.vectorstores, llm: langchain_openai.chat_models) -> Struct:
    """
    Create a conversation question/answer agent using the specified db and llm
    """
    struct = Struct(0, None, [])

    struct.chain = langchain.chains.ConversationalRetrievalChain.from_llm(
        llm,
        retriever=db.as_retriever(),
        return_source_documents=True,
        verbose=False,
    )

    return struct
