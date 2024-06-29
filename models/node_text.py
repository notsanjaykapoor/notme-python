import dataclasses


@dataclasses.dataclass
class NodeText:
    id: str
    file_name: str
    page_label: str
    text: str
    score: float = 0.0

    @property
    def meta(self) -> dict:
        return {
            "file_name": self.file_name,
            "node_type": "txt",
            "page_label": self.page_label,
            "text": self.text,
        }

    def text_index(self) -> str:
        """
        node's text that is indexable
        """
        return self.text
