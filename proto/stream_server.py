from concurrent import futures

import grpc
import stream_pb2_grpc


class StreamService(stream_pb2_grpc.StreamServicer):
    def rpc_stream(self, request_iterator, context):
        for message in request_iterator:
            yield message


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    stream_pb2_grpc.add_StreamServicer_to_server(StreamService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
