import sys  # noqa: E402

import ulid  # noqa: E402
from fastapi import FastAPI, WebSocket  # noqa: E402

import context
import dot_init  # noqa: F401
import log  # noqa: E402
import models
import services.ws  # noqa: E402
import services.ws.chat  # noqa: E402

logger = log.init("app")

socket_manager = models.SocketManager()

app = FastAPI()


@app.websocket("/ws/chat/{user_id}")
async def websocket_chat_endpoint(websocket: WebSocket, user_id: str):
    await services.ws.chat.Server(socket_manager, websocket, user_id).call()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        # generate request id for this connection
        context.rid_set(ulid.new().str)

        logger.info(f"{context.rid_get()} api.ws connected")

        await services.ws.Reader(websocket).call()
    except Exception:
        logger.info(f"{context.rid_get()} api.ws exception {sys.exc_info()[0]}")
