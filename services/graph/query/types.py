import dataclasses


@dataclasses.dataclass
class GraphQuery:
    query: str
    params: dict
