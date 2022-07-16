import typing


class Handler(typing.Protocol):
    # circular import error when using models.KafkaMessage, so use typing.Any as temporary fix
    async def call(self, msg: typing.Any) -> typing.Any:
        """process message"""
