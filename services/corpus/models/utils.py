import json
import os


def get_dimensions(model: str) -> int:
    """
    return model dimensions from config.json or 0 if there is no config or its not a local model
    """
    if not model.startswith("local:"):
        return 0

    _, model_name = model.split(":")
    models_root = os.environ["APP_MODELS_PATH"]
    models_path = f"{models_root}/{model_name}"

    if not os.path.exists(models_path):
        raise ValueError(f"model not found {models_path}")

    config_json = json.load(open(f"{models_path}/config.json"))
    
    return config_json.get("hidden_size", 0)


# deprecated?
def get_local_models() -> list[str]:
    """
    return list of local models
    """
    models_root = os.environ["APP_MODELS_PATH"]
    return os.listdir(models_root)
