import dataclasses
import time


@dataclasses.dataclass
class StructResponse:
    code: int
    msec: int
    response: str
    errors: list[str]


def prompt(scope: str, query: str) -> str:
    """
    return llm prompt from scope + query
    """
    return f"""
        Context information is below.
        ---------------------
        {scope}
        ---------------------
        Given the context information and not prior knowledge, answer the query.
        Query: {query}
        Answer:
    """


def query(llm, scope: str, question: str) -> StructResponse:
    """
    """
    struct = StructResponse(0, 0, "", [])

    t_start = time.time()

    llm_response = llm(f"""
        Context information is below.
        ---------------------
        {scope}
        ---------------------
        Given the context information and not prior knowledge, answer the query.
        Query: {question}
        Answer:
        """,
        max_tokens=None,
        stop=["Q:", "\n"], # Stop generating just before the model would generate a new question
        temperature=0.1,
    )
    print(llm_response)

    llm_choices = llm_response.get("choices")

    struct.response = llm_choices[0].get("text")
    struct.msec = (time.time() - t_start) * 1000

    return struct
