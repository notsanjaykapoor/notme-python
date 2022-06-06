import typing


def graph_value_query(type_name: str, type_value: str) -> typing.Union[int, str]:
    if type_name == "integer":
        # query as int
        return int(type_value)
    else:
        # query with quotes
        return f"'{type_value.lower()}'"
