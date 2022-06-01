import grpc
import unary_pb2_grpc as pb2_grpc
import unary_pb2 as pb2


class UnaryClient(object):
    """
    Client for gRPC functionality
    """

    def __init__(self, port: int):
        self.host = "localhost"
        self.server_port = port

        # instantiate a channel
        self.channel = grpc.insecure_channel(
            "{}:{}".format(self.host, self.server_port)
        )

        # bind the client and the server
        self.stub = pb2_grpc.UnaryStub(self.channel)

    def call(self, message):
        """
        Client function to call the rpc for GetServerResponse
        """
        message = pb2.Message(message=message)
        print(f"{message}")
        return self.stub.GetServerResponse(message)


if __name__ == "__main__":
    client = UnaryClient(port=50051)
    result = client.call(message="Hello Server you there?")
    print(f"{result}")
