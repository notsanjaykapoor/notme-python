from dotenv import load_dotenv

load_dotenv()

import json
import os
import sys
import typer

from sqlalchemy import func
from sqlmodel import select, Session, SQLModel

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from database import engine
from log import logging_init

import models
import services.db
import services.entities
import services.memgraph
import services.neo

logger = logging_init("cli")

app = typer.Typer()


# db dependency
def get_db():
    with Session(engine) as session:
        yield session


@app.command()
def entity_count():
    with Session(engine) as db:
        count = db.exec(select([func.count(models.Entity.id)])).one()

    logger.info(f"[db-cli] entity_count {count}")


@app.command()
def entity_import(
    file: str = typer.Option(...),
    truncate: bool = typer.Option(...),
):
    objects = json.load(open(file))

    logger.info(f"[db-cli] file {file} objects {len(objects)} truncate {truncate}")

    with Session(engine) as db:
        if truncate:
            services.db.truncate_table(db=db, table_name="entities")
            logger.info(f"[db-cli] entities truncated")

        struct = services.entities.Slurp(db=db, objects=objects).call()

        logger.info(f"[db-cli] imported {struct.count}")


if __name__ == "__main__":
    app()
