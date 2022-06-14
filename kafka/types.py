import dataclasses


@dataclasses.dataclass
class KafkaResult:
    code: int
    errors: list[str]
