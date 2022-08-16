def transform_first_last(object: dict, model_name: str, model_slugs: list[str]) -> dict:
    try:
        # transform only uses a single slug
        slug = model_slugs[0]
        name_slug = f"{model_name}.{slug}"

        value = object[name_slug]["value"]
        first_name, last_name = value.split(" ")

        object[f"{model_name}.first_name"] = {
            "value": first_name,
            "type": "unknown",  # todo
        }
        object[f"{model_name}.last_name"] = {
            "value": last_name,
            "type": "unknown",  # todo
        }
    except Exception:
        # set default values
        object[f"{model_name}.first_name"] = {
            "value": "error",
            "type": "error",
        }
        object[f"{model_name}.last_name"] = {
            "value": "error",
            "type": "error",
        }

    return object
