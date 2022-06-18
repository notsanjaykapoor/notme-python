import socket
import sys


def ping(host: str, port: int) -> int:
    try:
        s = socket.socket()
        s.connect((host, port))
        s.close()

        return 0
    except Exception:
        print(sys.exc_info()[0])

        return 1
