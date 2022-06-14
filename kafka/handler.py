import abc
import typing


class Handler(abc.ABC):
    @abc.abstractmethod
    # circular import error when using models.KafkaMessage, so use typing.Any as temporary fix
    async def call(self, msg: typing.Any) -> typing.Any:
        pass
