import dataclasses

import langchain.agents
import langchain_community
import langchain_community.embeddings
import langchain_openai.chat_models
from langchain import hub


@dataclasses.dataclass
class Struct:
    code: int
    agent: langchain.agents
    agent_executor: langchain.agents.AgentExecutor
    errors: list[str]


def chat_agent(db_name: str, embedding: langchain_community.embeddings, prompt_name: str) -> Struct:
    """
    Create a chat agent using the specified embedding and vector store to answer queries.
    """
    struct = Struct(0, None, None, [])

    db = langchain_community.vectorstores.FAISS.load_local(db_name, embedding, allow_dangerous_deserialization=True)

    tool = langchain.agents.agent_toolkits.create_retriever_tool(
        db.as_retriever(),
        "retriever",
       f"search and returns documents about {db_name}"
    )
    tools = [tool]

    llm = langchain_openai.chat_models.ChatOpenAI(temperature = 0)
    prompt = hub.pull(prompt_name)

    struct.agent = langchain.agents.create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)
    struct.agent_executor = langchain.agents.AgentExecutor(agent=struct.agent, tools=tools)

    return struct