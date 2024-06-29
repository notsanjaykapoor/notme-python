import dataclasses


@dataclasses.dataclass
class NodeImage:
    caption: str
    id: str
    name: str
    uri: str
    score: float = 0.0

    @property
    def id_(self) -> str:
        return self.id

    @property
    def meta(self) -> dict:
        return {
            "caption": self.caption,
            "name": self.name,
            "node_type": "img",
            "uri": self.uri,
        }
    
    def text_index(self) -> str:
        """
        node's text that should be indexed
        """
        texts = [s.strip() for s in [self.name, self.caption] if s]

        return ". ".join(texts)

        