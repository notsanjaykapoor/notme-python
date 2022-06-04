from dotenv import load_dotenv

load_dotenv()

import logging
import os
import sys
import ulid
import zerorpc

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from database import engine
from dataclasses import dataclass, field
from log import logging_init
from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket
from sqlmodel import Session, SQLModel

import services.zero.rpc

from context import request_id


logger = logging_init("cli")


def rpc_server(port: int = 4242):
    logger.info(f"rpc_server port {port} starting")

    s = zerorpc.Server(services.zero.rpc.User())
    s.bind(f"tcp://0.0.0.0:{port}")
    s.run()


if __name__ == "__main__":
    rpc_server()
