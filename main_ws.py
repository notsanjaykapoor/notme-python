from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import contextvars
import logging
import strawberry
import sys
import ulid

from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket

import services.ws
import services.ws.chat

from context import request_id
from log import logging_init
from models.socket_manager import SocketManager

logger = logging_init("api")

socket_manager = SocketManager()

app = FastAPI()


@app.websocket("/ws/chat/{user_id}")
async def websocket_chat_endpoint(websocket: WebSocket, user_id: str):
    await services.ws.chat.Server(socket_manager, websocket, user_id).call()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        # generate request id for this connection
        request_id.set(ulid.new().str)

        logger.info(f"{request_id.get()} api.ws connected")

        await services.ws.Reader(websocket).call()
    except:
        logger.info(f"{request_id.get()} api.ws exception {sys.exc_info()[0]}")
