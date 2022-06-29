import asyncio

import pytest

from models import Actor


class ActorHandler:
    def __init__(self, app_name: str) -> None:
        self._app_name = app_name

    # process actor message
    def call(self, actor: Actor, message: dict):
        print(f"[actor {self._app_name}] {message}")


@pytest.mark.asyncio
async def test_actor():
    print("test_actor")

    name = "actor-1"
    queue = asyncio.Queue(maxsize=0)
    handler = ActorHandler(app_name=name)
    actor = Actor(name=name, queue=queue, handler=handler)

    result = actor.schedule()

    assert result == 0

    queue.put_nowait({"name": "hello"})
    await queue.join()

    assert queue.qsize() == 0

    actor.cancel()
