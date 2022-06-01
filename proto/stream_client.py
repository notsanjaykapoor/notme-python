from __future__ import print_function

import grpc
import stream_pb2
import stream_pb2_grpc


def make_message(message: str) -> stream_pb2.Message:
    return stream_pb2.Message(message=message)


def generate_messages():
    messages = [
        make_message("message 1"),
        make_message("message 2"),
        make_message("message 3"),
        make_message("message 4"),
        make_message("message 5"),
    ]
    for msg in messages:
        print(f"client sending '{msg.message}'")
        yield msg


def send_message(stub: stream_pb2_grpc.StreamStub):
    responses = stub.rpc_stream(generate_messages())

    for response in responses:
        print(f"client received '{response.message}'")


def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = stream_pb2_grpc.StreamStub(channel)
        send_message(stub)


if __name__ == "__main__":
    run()
