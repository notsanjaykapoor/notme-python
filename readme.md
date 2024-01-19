### Intro

This repo is a collection of interesting python networking and database tools and libraries with sample code.

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

### FastAPI Example

[FastAPI](https://fastapi.tiangolo.com/) s a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints.

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

### FastAPI Chat Example

The chat example implements a chat server using FastAPI and websockets. You need to run at least 2 console users to really see this work.

Start the server first:

```
./scripts/ws-server
```

Start 2 consoles in separate terminals with different user ids and send messages:

```
./tty/ws-console --user-id user-1

./tty/ws-console --user-id user-2
```

### Redpanda (Kafka) Example

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

Run the server and then the client in 2 separate terminals:

```
./tty/crypto-server --app crypto

./tty/crypto-client --topic crypto
```

The chess example using a chess pgn file.

Create 'chess' topic:

```
rpk topic create chess --brokers=redpanda-dev:9092
```

Run the server and then the client in 2 separate terminals:

```
./tty/chess-kafka-server --app chess

./tty/chess-kafka-client --topic chess --file ./data/chess/mega2400_part_01.pgn.txt --max-records 1000000000
```

Publish general kafka message to a specific topic:

```
./tty/py-cli topic-write --topic test --brokers=redpanda-dev:9092
```


### ZeroMQ Example

[ZeroMQ](https://zeromq.org/) looks like an embeddable networking library but acts like a concurrency framework. It gives you sockets that carry atomic messages across various transports like in-process, inter-process, TCP, and multicast. You can connect sockets N-to-N with patterns like fan-out, pub-sub, task distribution, and request-reply. It's fast enough to be the fabric for clustered products. Its asynchronous I/O model gives you scalable multicore applications, built as asynchronous message-processing tasks. It has a score of language APIs and runs on most operating systems.

This zeromq example is using push/pull sockets to implement a pipeline algorithm using a chess pgn file. There are 3 steps in the pipeline, the source, the filter, and the sink.

Start the sink, then the filter, and then the source in 3 separate terminals:

```
./tty/chess-zero-sink

./tty/chess-zero-filter

./tty/chess-zero-source
```


### Zerorpc Example

[Zerorpc](https://www.zerorpc.io/) is a light-weight, reliable and language-agnostic library for distributed communication between server-side processes. It builds on top of ZeroMQ and MessagePack. Support for streamed responses - similar to python generators - makes zerorpc more than a typical RPC engine. Built-in heartbeats and timeouts detect and recover from failed requests. Introspective capabilities, first-class exceptions and the command-line utility make debugging easy.

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

