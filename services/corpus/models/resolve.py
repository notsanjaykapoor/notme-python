import os

import llama_index.embeddings
import llama_index.embeddings.clip
import llama_index.embeddings.huggingface


def resolve(model: str, device: str) -> llama_index.embeddings:
    """
    resolve model name to llama_index embed model
    """
    if model.startswith("local:"):
        # local model
        _, model_name = model.split(":")
        models_root = os.environ["APP_MODELS_PATH"]
        model_path = f"{models_root}/{model_name}"

        if not os.path.exists(model_path):
            raise ValueError(f"model path not found '{model_path}'")

        # use huggingface model from local models directory
        embed_model = llama_index.embeddings.huggingface.HuggingFaceEmbedding(
            device=device,
            model_name=model_path,
            trust_remote_code=True,
        )
    elif model.startswith("clip:"):
        # clip model, download and cache, default cache is ~/.cache
        _, model_name = model.split(":")

        if model_name == "default":
            model_name = "ViT-B/32"

        embed_model = llama_index.embeddings.clip.ClipEmbedding(
            device=device,
            model_name=model_name,
            trust_remote_code=True,
        )
    else:
        raise ValueError(f"invalid model '{model}'")

    return embed_model
