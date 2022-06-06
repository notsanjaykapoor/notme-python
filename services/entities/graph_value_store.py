import typing


def graph_value_store(type_name: str, type_value: str) -> typing.Union[int, str]:
    if type_name == "integer":
        # store as int
        return int(type_value)
    else:
        return type_value.lower()
