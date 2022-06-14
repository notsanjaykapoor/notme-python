#!/usr/bin/env python

import os
import sys

import dotenv
import typer
import ulid

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import kafka  # noqa: E402
import log  # noqa: E402

dotenv.load_dotenv()

app = typer.Typer()

logger = log.logging_init("cli")


@app.command()
def chess_client(
    topic: str = typer.Option(...),
    file: str = typer.Option(...),
    max_records: int = 2**30,
):
    writer = kafka.Writer(topic=topic)

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
