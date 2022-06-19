import typing

import sqlalchemy
import sqlmodel


class EntityWatch(sqlmodel.SQLModel, table=True):  # type: ignore
    __tablename__ = "entity_watches"
    __table_args__ = (sqlalchemy.UniqueConstraint("message", "query", "topic", name="_message_query_topic_unique"),)

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    message: str = sqlmodel.Field(index=True)
    output: str = sqlmodel.Field(index=True)
    query: str = sqlmodel.Field(index=True)
    topic: str = sqlmodel.Field(index=True)

    def pack(self) -> dict:
        return {
            "id": self.id,
            "message": self.message,
            "output": self.output,
            "query": self.query,
            "topic": self.topic,
        }
