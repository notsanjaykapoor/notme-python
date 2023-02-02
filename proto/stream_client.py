from __future__ import print_function

import asyncio

import grpc
import stream_pb2
import stream_pb2_grpc


async def message_send(call: grpc.aio.Call, count: int):
    print("[message_send] coroutine starting")

    for i in range(0, count):
        print(f"[message_send] {i}")
        proto_message = stream_pb2.Message(message=f"message {i}")
        await call.write(proto_message)

    # await call.done_writing()
    print("[message_send] coroutine exiting")


async def message_receive(call: grpc.aio.Call):
    print("[message_receive] coroutine starting")

    async for object in call:
        if type(object) is stream_pb2.Message:
            print(f"[message_receive] {object.message}")

    print("[message_receive] coroutine exiting")


async def main(port=50051):
    async with grpc.aio.insecure_channel(f"localhost:{port}") as channel:
        async_stub = stream_pb2_grpc.StreamStub(channel)
        async_call = async_stub.rpc_message()

        task_rx = asyncio.create_task(message_receive(async_call))
        task_send = asyncio.create_task(message_send(async_call, 10))

        await task_send
        await task_rx


if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(main())
