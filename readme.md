### Setup

Install python 3.11.6.

Create python virtual env:

```
pyenv virtualenv 3.11.6 notme
pyenv activate notme
```

Install python packages:

```
pip install -r requirements.txt
```

### Api Example

Start server:

```
./scripts/py-api -p 8001
```

List users using curl (api server required):

```
curl http://127.0.0.1:8001/api/v1/users
```

List users using python client (api server not required):

```
./tty/py-cli user-search
```

Create user (api server not required):

```
./tty/py-cli.py user-create --name user-1
```

### Chat Example

The chat example uses a chat server and a client/console. You need to run at least 2 console users to really see this work.

Start the server first:

```
./scripts/ws-server
```

Start 2 consoles with different user ids and send messages:

```
./tty/ws-console --user-id user-1

./tty/ws-console --user-id user-2
```

### Redpanda

Redpanda install:

Install rpk binary:

```
brew install redpanda-data/tap/redpanda
```

Redpanda topic list:

```
rpk topic list --brokers=redpanda-dev:9092
```

The crypto example uses an actor based server that reads from a kafka topic with a set of actors to process each message.

Create 'crypto' topic:

```
rpk topic create crypto --brokers=redpanda-dev:9092
```

Run the server and then the client:

```
./tty/crypto-server --app crypto

./tty/crypto-client --topic crypto
```

The chess example ...

Create 'chess' topic:

```
rpk topic create chess --brokers=redpanda-dev:9092
```

Run the server and then the client:

```
./tty/chess-kafka-server.py --app chess

./tty/chess-kafka-client.py --topic chess --file ./data/chess/mega2400_part_01.pgn.txt --max-records 1000000000
```

The benchmarks for this example comparing kafka vs redpanda:

1. kafka - 10000 records ~ 18 mins, all 35273 records ~ 66 mins (on power)

2. redpanda - 10000 records ~ 17 mins, all 35273 records ~ 63 mins (on battery)

Publish general kafka message to a specific topic:

```
./tty/py-cli topic-write --topic test --brokers=redpanda-dev:9092
```

### Zerorpc Example

The zerorpc examples uses rpc to implement a simple users service.

Start the server first (defaults to port 4242):

```
./tty/rpc-server
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

This zeromq example is using push/pull sockets to implement a pipeline algorithm. There are 3 steps in the pipeline, the source, the filter, and the sink.

Start the sink, then the filter, and then the source:

```
./tty/chess-zero-sink

./tty/chess-zero-filter

./tty/chess-zero-source
```

### Curio Example 

[Curio](https://curio.readthedocs.io/en/latest/index.html) is a library for concurrent systems programming that uses coroutines and common programming abstractions such as threads, sockets, files, locks, and queues. In addition, it supports cancellation, task groups, and other useful features

This example uses curio channels between a producer and consumer to send messages from a chess pgn file.

Start the producer first:

```
./tty/chess-curio-source
```

Then start the consumer:

```
./tty/chess-curio-sink
```

### GRPC Example

[gRPC](https://grpc.io/) is a modern open source high performance Remote Procedure Call (RPC) framework that can run in any environment. It can efficiently connect services in and across data centers with pluggable support for load balancing, tracing, health checking and authentication.

This example uses a grpc stream to send messages from a chess pgn file.

Compile proto file:

```
./scripts/grpc/grpc-compile proto/chess.proto
```

Run the chess server:

```
python proto/chess_server.py
```

Then run the stream client:

```
python proto/chess_client.py
```

### Neo4j Example

Start container:

```
docker-compose -f docker-compose-neo4j.yml up -d
```

Show databases:

```
show databases;
```

Create database:

```
create database notme.dev;
```

Reset database:

```
create or replace database neo4j;
```

Use database:

```
:use notme.dev;
```

Start cypher shell:

```
cypher-shell --addres neo4j://localhost:13687 -u neo4j
```

Load graph data:

```
./c/db-cli boot reset --file ./data/notme/entities/entities.json
```

Total nodes: 3169
Total relationships: 9742

