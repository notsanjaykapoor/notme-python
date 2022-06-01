from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import asyncio
import json
import logging
import signal
import time
import typer
import ulid
import uvloop
import websocket

from database import engine
from sqlmodel import Session, SQLModel
from typing import Optional

from actors.example.app import App

from kafka.reader import KafkaReader
from kafka.writer import KafkaWriter

from log import logging_init

app = typer.Typer()

logger = logging_init("cli")


@app.command()
def chess_client(
    topic: str = typer.Option(...),
    file: str = typer.Option(...),
    max_records: int = 2**30,
):
    writer = KafkaWriter(topic=topic)

    with open(file, mode="r", encoding="ISO-8859-1") as f:
        msg_count = 0

        for line in f:
            if "Result" not in line:
                continue

            # write message to kafka stream
            writer.call(
                key=ulid.new().str,
                message=line,
            )

            msg_count += 1

            if msg_count >= max_records:
                break

        # write eof marker
        writer.call(
            key=ulid.new().str,
            message="eof",
        )

        logger.info(f"message count {msg_count}")


if __name__ == "__main__":
    app()
