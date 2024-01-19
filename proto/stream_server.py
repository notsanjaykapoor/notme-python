from concurrent import futures

import grpc
import stream_pb2_grpc


class StreamService(stream_pb2_grpc.StreamServicer):
    def rpc_message(self, request_iterator, context):
        for message in request_iterator:
            print(f"rx: {message}")
            yield message


def serve(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    stream_pb2_grpc.add_StreamServicer_to_server(StreamService(), server)

    print(f"server starting port {port}")

    server.add_insecure_port(f"[::]:{port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
