import typing

import sqlalchemy
import sqlmodel


class EntityWatch(sqlmodel.SQLModel, table=True):  # type: ignore
    __tablename__ = "entity_watches"
    __table_args__ = (sqlalchemy.UniqueConstraint("query", "topic", name="_query_topic_unique"),)

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    output: str = sqlmodel.Field(index=True)
    query: str = sqlmodel.Field(index=True)
    topic: str = sqlmodel.Field(index=True)

    def pack(self) -> dict:
        return {
            "id": self.id,
            "output": self.output,
            "query": self.query,
            "topic": self.topic,
        }
