import dataclasses
import os

import llama_cpp
import llama_cpp.llama_chat_format

@dataclasses.dataclass
class Struct:
    code: int
    response: dict
    text: str


def caption(uri: str) -> Struct:
    """
    run one shot query to caption the specified image
    """
    struct = Struct(
        code=0,
        response={},
        text="",
    )

    chat_handler = llama_cpp.llama_chat_format.Llava16ChatHandler(
        clip_model_path=os.environ.get("APP_MODEL_CLIP_PATH"),
    )

    llm = llama_cpp.Llama(
        chat_handler=chat_handler,
        model_path=os.environ.get("APP_LLM_MULTI_PATH"),
        n_ctx=4096, # large context for image embeddings
        verbose=False,
    )

    llm_response = llm.create_chat_completion(
        messages = [
            {
                "role": "system",
                "content": "You are an assistant who perfectly describes images."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type" :"text",
                        "text": "Describe this image with a short caption.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": uri },
                    },
                ]
            }
        ],
        temperature=0.1, # default is 0.2
    )

    struct.response = llm_response
    struct.text = llm_response.get("choices")[0].get("message").get("content").strip()

    return struct
