from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import asyncio
import json
import logging
import os
import signal
import sys
import time
import typer
import ulid
import uvloop
import websocket

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from database import engine
from sqlmodel import Session, SQLModel
from typing import Optional

import services.crypto.pkey
import services.users

from actors.example.app import App
from actors.handlers.generic import HandlerGeneric as ActorHandler

from kafka.handlers.generic import HandlerGeneric as KafkaHandler
from kafka.reader import KafkaReader
from kafka.writer import KafkaWriter

from log import logging_init
from models import user


logger = logging_init("cli")

app = typer.Typer()


@app.command()
def actor_client(topic: str = typer.Option(...)):
    writer = KafkaWriter(topic=topic)

    file = f"{topic}.json"  # e.g. example.json
    data = json.load(open(file))

    for record in data:
        # write to kafka stream
        writer.call(
            key=ulid.new().str,
            message=record,
        )

        break


@app.command()
def actor_server(app: str = typer.Option(...), msg: str = "ping"):
    uvloop.install()
    asyncio.run(actor_server_async(app=app, msg=msg))


async def actor_server_async(app: str, msg: str):
    logger.info(f"cli actor_server starting")

    # start app
    struct_app = App(toml_file=f"./data/apps/{app}.toml").call()

    # get app actors
    actors = [actor for name, actor in struct_app.actors.items()]

    def signal_handler(signum, frame):
        logger.info(f"cli actor_server signal handler ... cleaning up")
        for actor in actors:
            actor.cancel()

    # install signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # wait on tasks
    logger.info(f"cli actor_server wait on {len(actors)} actors")

    try:
        tasks = [actor.task for actor in actors]
        await asyncio.gather(*tasks)
    except:
        logger.error(f"cli actor_server exception {sys.exc_info()[0]}")

    # actor_source = struct_manager.actors["source"]
    #
    # message = {
    #   "message": msg,
    # }
    #
    # r = range(5)
    #
    # for i in r:
    #   await asyncio.sleep(3)
    #
    #   message["index"] = i
    #   message["rid"] = ulid.new().str
    #
    #   actor_source.queue.put_nowait(message)


@app.command()
def crypto_sign(data: str = "secret"):
    struct_pkey = services.crypto.pkey.Create().call()

    private_key = struct_pkey.key
    public_key = private_key.public_key()

    struct_sign = services.crypto.pkey.Sign(private_key, data).call()

    logger.info(f"cli sign {struct_sign}")

    signature = struct_sign.encoded

    struct_verify = services.crypto.pkey.Verify(
        public_key,
        data,
        signature,
    ).call()

    logger.info(f"cli verify {struct_verify}")


@app.command()
def json_rewrite(file: str = "./data/example/example.json"):
    logger.info(f"cli json_rewrite file {file}")

    data = json.load(open(file))
    records = []
    with open("./data/example/graph.json", "w") as output:
        for record in data:
            record["id"] = ulid.new().str
            records.append(record)

        output.write(json.dumps(records))


@app.command()
def topic_read(topic: str = typer.Option(...), group: str = "python"):
    # call reader with generic handler
    handler = KafkaHandler()
    reader = KafkaReader(topic, group, handler)
    reader.call()


@app.command()
def topic_write(topic: str = typer.Option(...), key: str = typer.Option(...)):
    # todo: use async?

    writer = KafkaWriter(topic=topic)

    writer.call(
        key=key,
        message={
            "message": "ping",
            "rid": ulid.new().str,
        },
    )


@app.command()
def user_create(name: str = typer.Option(...)):
    logger.info(f"cli user {name} create try")

    with Session(engine) as db_session:
        struct_get = services.users.Get(db=db_session, user_id=name).call()

        if struct_get.user:
            logger.info(f"cli result user {name} exists")
            return 0

        struct_create = services.users.Create(db=db_session, user_id=name).call()

        if struct_create.code == 0:
            logger.info(f"cli result user {name} created")

        return struct_create.user_id


@app.command()
def user_search(query: str = ""):
    with Session(engine) as db_session:
        service = services.users.List(db_session, query, 0, 10)
        struct = service.call()

        for user in struct.users:
            logger.info(f"cli result {user}")


@app.command()
def ws_send(message: str = "hey"):
    logger.info(f"cli websocket sending '{message}'")

    ws = websocket.WebSocket()
    ws.connect(f"{os.environ['WS_URL']}/ws")
    ws.send(message)
    ws.close()


if __name__ == "__main__":
    app()
