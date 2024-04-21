import dataclasses

import langchain.agents
import langchain.agents.agent_toolkits
import langchain_community
import langchain_community.embeddings
import langchain_community.vectorstores
import langchain_openai.chat_models

from langchain import hub


@dataclasses.dataclass
class Struct:
    code: int
    agent: langchain.agents
    agent_executor: langchain.agents.AgentExecutor
    errors: list[str]


def chat_agent(
        db: langchain_community.vectorstores,
        llm: langchain_openai.chat_models,
        prompt: hub,) -> Struct:
    """
    Create a chat agent using the specified db, embedding, llm and prompt
    """
    struct = Struct(0, None, None, [])

    tool = langchain.agents.agent_toolkits.create_retriever_tool(
        db.as_retriever(),
        "retriever",
        "rag implementation",
    )
    tools = [tool]

    struct.agent = langchain.agents.create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)
    struct.agent_executor = langchain.agents.AgentExecutor(agent=struct.agent, tools=tools)

    return struct