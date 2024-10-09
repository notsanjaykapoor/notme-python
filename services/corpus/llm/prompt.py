import dataclasses


@dataclasses.dataclass
class StructResponse:
    code: int
    msec: int
    response: str
    errors: list[str]


def prompt_image_caption(image_url: str) -> str:
    """
    return prompt string using a prompt template

    template docs: https://llava-vl.github.io/
    """
    return f"""
        Context information is below.
        ---------------------
        {image_url}
        ---------------------
        Given the context information and not prior knowledge, answer the query.
        Query: Describe this image in a very detailed way.
        Answer:
    """


def prompt_text(scope: str, query: str) -> str:
    """
    return prompt string using a prompt template

    template docs: https://www.llama.com/docs/how-to-guides/prompting
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


def _prompt_image_caption_v1(image_url: str) -> str:
    """
    return prompt string using a prompt template

    template docs: https://llava-vl.github.io/
    """
    return f"""
        User: {image_url}
        Describe this image without interpretations.
    """
