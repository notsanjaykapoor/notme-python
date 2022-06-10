import typing


def graph_value(type_name: str, type_value: str) -> typing.Union[int, str]:
    # query with quotes
    return f"'{type_value.lower()}'"
