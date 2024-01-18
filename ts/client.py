import os

import typesense


def client(uri: str, api_key: str) -> typesense.Client:
    proto, host, port = uri.split(":")
    host = host.replace("/", "")

    client = typesense.Client(
        {
            "nodes": [
                {
                    "host": host,
                    "port": port,
                    "protocol": proto,
                }
            ],
            "api_key": api_key,
            "connection_timeout_seconds": 2,
        }
    )

    return client


def client_default() -> typesense.Client:
    return client(
        uri=client_default_uri(),
        api_key=os.environ.get("TYPESENSE_API_KEY"),
    )


def client_default_uri() -> str:
    return os.environ.get("TYPESENSE_URL")
