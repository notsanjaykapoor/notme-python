from dotenv import load_dotenv

load_dotenv() # take environment variables from .env.

import os
import pdb
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import asyncio
import json
import logging
import signal
import time
import typer
import ulid
import uvloop
import websocket

from cryptography.hazmat.primitives import serialization
from database import engine
from sqlmodel import Session, SQLModel
from typing import Optional

from log import logging_init

from kafka.reader import KafkaReader
from kafka.writer import KafkaWriter

from services.crypto.pkey.rsa.sign import RsaSign
from services.crypto.pkey.rsa.verify import RsaVerify
from services.crypto.pkey.type import key_type

app = typer.Typer()

logger = logging_init("cli")

@app.command()
def sign(pem_private: str = typer.Option(...), message: str = typer.Option(...)):
  # read pem file and convert to bytes
  pem_str = open(pem_private, "r").read()
  pem_bytes = pem_str.encode("utf-8")

  private_key = serialization.load_pem_private_key(pem_bytes, password=None)

  logger.info(f"private_key {key_type(private_key)}")

  # pdb.set_trace()

  struct_sign = RsaSign(
    private_key,
    message
  ).call()

  logger.info(f"sign {struct_sign}")

  return struct_sign

@app.command()
def sign_verify(pem_private: str = typer.Option(...), pem_public: str = typer.Option(...), message: str = typer.Option(...)):
  # sign

  struct_sign = sign(pem_private, message)

  # read pem file and convert to bytes
  pem_str = open(pem_public, "r").read()
  pem_bytes = pem_str.encode("utf-8")

  public_key = serialization.load_pem_public_key(pem_bytes)

  logger.info(f"public_key {key_type(public_key)}")

  struct_verify = RsaVerify(
    public_key,
    message,
    signature = struct_sign.encoded,
  ).call()

  logger.info(f"struct_verify {struct_verify}")

if __name__ == "__main__":
  app()
