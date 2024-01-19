from concurrent import futures

import grpc
import chess_pb2
import chess_pb2_grpc


class ChessService(chess_pb2_grpc.StreamServicer):
    def message(self, request_iterator, context):
        msg_dict = {}
        msg_count = 0

        for struct in request_iterator:
            match struct.subject:
                case "chess-data":
                    message = struct.message

                    if "Result" in message:
                        if not message in msg_dict.keys():
                            msg_dict[message] = 0

                        msg_dict[message] += 1

                    msg_count += 1

                    if msg_count % 50000 == 0:
                        print(f"rx: chess-data count {msg_count}")

                case "chess-end":
                    print(f"rx: {struct.subject} {msg_dict}")
                    yield chess_pb2.Message(subject="chess-result", message=str(msg_dict))

                case "chess-start":
                    print(f"rx: {struct.subject}")


def serve(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chess_pb2_grpc.add_StreamServicer_to_server(ChessService(), server)

    print(f"chess server starting on port {port}")

    server.add_insecure_port(f"[::]:{port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
