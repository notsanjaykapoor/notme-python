import dataclasses


@dataclasses.dataclass
class NodeImage:
    caption: str
    id: str
    name: str
    uri: str
    score: float = 0.0


    @property
    def image_thumb_uri(self, transform="tr:w-225,h-150") -> str:
        img_tokens = self.uri.split("/")
        img_prefix = "/".join(img_tokens[0:-1])
        return f"{img_prefix}/{transform}/{img_tokens[-1]}"


    @property
    def meta(self) -> dict:
        return {
            "caption": self.caption,
            "name": self.name,
            "node_type": "img",
            "uri": self.uri,
        }

    @property
    def text(self) -> str:
        """
        image node's text
        """
        texts = [s.strip() for s in [self.name, self.caption] if s]

        return ". ".join(texts)

    @property
    def text_indexable(self) -> str:
        """
        image node's indexable text
        """
        return self.text

        