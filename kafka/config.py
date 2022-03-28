import os
import socket

config = {
  "bootstrap.servers": os.environ.get("KAFKA_BROKERS"),
  "client.id": socket.gethostname(),
}
