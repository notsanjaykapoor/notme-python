### Setup

All dependencies are managed by poetry, and requires python 3.10 to run:

```
pip install poetry

poetry install
```


### Api Example

Start server:

```
./scripts/py-api
```

List users using curl:

```
curl http://127.0.0.1:8001/users
```

List users using python client:

```
poetry run ./runners/py-cli.py user-search
```

Create user:

```
poetry run ./runners/py-cli.py user-create user-1
```


### Chat Example

The chat example uses a chat server and a client/console.  You need to run at least 2 console users to really see this work.


Start the server first:

```
./scripts/ws-server
```

Start 2 consoles with different user ids and send messages:

```
poetry run python3 ./runners/ws-console.py --user-id user-1

poetry run python3 ./runners/ws-console.py --user-id user-2
```


### Kafka

The crypto example run an actor based server that reads from a kafka topic and uses a set of actors to process each message.

```
poetry run python3 runners/crypto-server.py --app crypto

poetry run python3 runners/crypto-client.py --topic crypto
```

The chess example ...

```
poetry run python3 runners/chess-kafka-server.py --app chess

poetry run python3 runners/chess-kafka-client.py --topic chess --file ./data/chess/mega2400_part_01.pgn.txt
```

Publish message:

```
poetry run ./runners/py-cli topic-write  --topic test
```


### Zerorpc Example

The zerorpc examples uses rpc to implement a simple users service.

Start the server first (defaults to port 4242):

```
poetry run python3 ./runners/rpc-server.py
```

Once the server is running, you can query it using the zerorpc client:

```
zerorpc tcp://127.0.0.1:4242
```

List all users:

```
zerorpc tcp://127.0.0.1:4242 users_list ""
```

Get user by id:

```
zerorpc tcp://127.0.0.1:4242 user_get "name"
```


### Zeromq Example

This zeromq example is using push/pull sockets to implement a pipeline algorithm.  There are 3 steps in the pipeline, the source, the filter, and the sink.  

Start the sink, then the filter, and then the source:

```
poetry run python3 runners/chess-zero-sink.py

poetry run python3 runners/chess-zero-filter.py

poetry run python3 runners/chess-zero-source.py
```

### Curio Channel

This example uses curio channels between a producer and consumer to send messages.

Start the producer first:

```
poetry run python3 runners/chess-curio-source.py
```

Then start the consumer:

```
poetry run python3 runners/chess-curio-sink.py
```
