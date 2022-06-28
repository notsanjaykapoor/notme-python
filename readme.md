### Setup

Install python 3.10.

Install python packages with pip:

```
pip install -r requirements.txt
```

### Ansible

Start containers:

```
ansible-playbook ./ansible/playbook.yml -i ./ansible/inventories/hosts
```

### Api Example

Start server:

```
./scripts/py-api
```

List users using curl (api server required):

```
curl http://127.0.0.1:8001/users
```

List users using python client (api server not required):

```
python ./runners/py-cli.py user-search
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
./tty/ws-console.py --user-id user-1

./tty/ws-console.py --user-id user-2
```

### Kafka + Redpanda

Kafka install:

```
docker-compose -f docker-compose-kafka.yml up -d
```

Kafka topic create:

```
docker exec -it broker kafka-topics --bootstrap-server broker:9092 --create --topic chess

docker exec -it broker kafka-topics --bootstrap-server broker:9092 --create --topic crypto

docker exec -it broker kafka-topics --bootstrap-server broker:9092 --list
```

Redpanda install:

Install rpk binary:

```
brew install redpanda-data/tap/redpanda
```

```
docker-compose -f docker-compose-redpanda.yml up -d

```

Redpanda topic create:

```
rpk topic create chess --brokers=localhost:9092

rpk topic create crypto --brokers=localhost:9092

rpk topic list --brokers=localhost:9092
```

The crypto example uses an actor based server that reads from a kafka topic with a set of actors to process each message.

Create 'crypto' topic (see above) before running this example.

```
./tty/crypto-server.py --app crypto

./tty/crypto-client.py --topic crypto
```

The chess example ...

Create 'chess' topic (see above) before running this example.

```
./tty/chess-kafka-server.py --app chess

./tty/chess-kafka-client.py --topic chess --file ./data/chess/mega2400_part_01.pgn.txt --max-records 1000000000
```

The benchmarks for this example comparing kafka vs redpanda:

1. kafka - 10000 records ~ 18 mins, all 35273 records ~ 66 mins (on power)

2. redpanda - 10000 records ~ 17 mins, all 35273 records ~ 63 mins (on battery)

Publish general kafka message to a specific topic:

```
./tty/py-cli topic-write  --topic test
```

### Zerorpc Example

The zerorpc examples uses rpc to implement a simple users service.

Start the server first (defaults to port 4242):

```
./tty/rpc-server.py
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
./tty/chess-zero-sink.py

./tty/chess-zero-filter.py

./tty/chess-zero-source.py
```

### Curio Channel

This example uses curio channels between a producer and consumer to send messages.

Start the producer first:

```
./tty/chess-curio-source.py
```

Then start the consumer:

```
./tty/chess-curio-sink.py
```

### GRPC Example

Compile proto file:

```
./scripts/grpc-compile proto/stream.proto
```

Run the stream server:

```
python proto/stream_server.py
```

Then run the stream client:

```
python proto/stream_client.py
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

### Memgraph Example

Docker install: (https://hub.docker.com/r/memgraph/memgraph)

```
docker-compose -f docker-compose-memgraph.yml up -d

```

Run mg_client interactive client in a python shell:

```
import mgclient

conn = mgclient.connect(host='127.0.0.1', port=7687)

cursor = conn.cursor()

query = "match (n) return count(*)"

cursor.execute(query); rows = cursor.fetchall(); rows
```

### Datadog

Docker install:

```
docker run -d --name dd-agent -v /var/run/docker.sock:/var/run/docker.sock:ro -v /proc/:/host/proc/:ro -v /sys/fs/cgroup/:/host/sys/fs/cgroup:ro -e DD_API_KEY=ca6d9d1162c1a0f3f22959d9d6a86afc -e DD_SITE="datadoghq.com" -e DD_DOGSTATSD_NON_LOCAL_TRAFFIC="true" -e DD_IGNORE_AUTOCONF="elastic istio redisdb" -p 8125:8125/udp gcr.io/datadoghq/agent:7
```
