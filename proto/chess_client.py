from __future__ import print_function

import asyncio

import grpc
import chess_pb2
import chess_pb2_grpc


async def message_send(call: grpc.aio.Call, file: str):
    print(f"[tx] coroutine starting ... file {file}")

    with open(file, mode="r", encoding="ISO-8859-1") as f:
        await call.write(chess_pb2.Message(subject="chess-start", message=""))
        print("[tx] chess-start")

        for line in f:
            await call.write(chess_pb2.Message(subject="chess-data", message=line.strip()))

    await call.write(chess_pb2.Message(subject="chess-end", message=""))
    await call.done_writing()

    print("[tx] chess-end")
    print("[tx] coroutine exiting")


async def message_receive(call: grpc.aio.Call):
    print("[rx] coroutine starting")

    async for struct in call:
        if struct.subject == "chess-result":
            print(f"[rx] {struct.message}")
            break

    print("[rx] coroutine exiting")


async def main(file: str, port=50051):
    async with grpc.aio.insecure_channel(f"localhost:{port}") as channel:
        async_stub = chess_pb2_grpc.StreamStub(channel)
        async_call = async_stub.message()

        task_rx = asyncio.create_task(message_receive(async_call))
        task_send = asyncio.create_task(message_send(async_call, file=file))

        await task_send
        await task_rx


if __name__ == "__main__":
    file = "./data/chess/mega2400_part_01.pgn.txt"

    asyncio.run(main(file=file))
