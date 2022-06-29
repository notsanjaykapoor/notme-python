import dataclasses
import typing

import models
import services.entity_watches
import services.mql


@dataclasses.dataclass
class Struct:
    code: int
    count: int
    errors: list[str]


class Publish:
    """publish entity messages for the specified watch and entity list"""

    def __init__(self, watches: list[models.EntityWatch], entity_ids: typing.Sequence[typing.Union[int, str]]):
        self._watches = watches
        self._entity_ids = entity_ids

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        for watch in self._watches:
            for entity_id in self._entity_ids:
                message = models.Entity.message_cls(id=entity_id, message=watch.message)

                struct_publish = services.entities.Publish(message=message, topic=watch.output).call()

                if struct_publish.code == 0:
                    struct.count += 1

        return struct
