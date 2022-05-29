import typing

# represents an incoming actor messge, a wrapper on top of a kafka message


class ActorMessage:
    def __init__(self, message: typing.Any):
        self._message = message

    def header(self):
        dict = {
            "key": self.key_str(),
            "offset": self._message.offset(),
            "partition": self._message.partition(),
            "topic": self._message.topic(),
        }

        return dict

    def key(self) -> bytes:
        return self._message.key()

    def key_str(self) -> str:
        return self._message.key().decode("utf-8")

    def offset(self) -> int:
        return self._message.offset()

    def partition(self) -> int:
        return self._message.partition()

    def topic(self) -> str:
        return self._message.topic()

    def value(self) -> bytes:
        return self._message.value()

    def value_str(self) -> str:
        return self._message.value().decode("utf-8")
