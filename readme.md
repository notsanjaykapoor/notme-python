### Setup

Install python 3.10.

Install python packages with pip:

```
pip install -r requirements.txt
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
python ./runners/py-cli.py user-search
```

Create user:

```
python ./runners/py-cli.py user-create --name user-1
```


### Chat Example

The chat example uses a chat server and a client/console.  You need to run at least 2 console users to really see this work.


Start the server first:

```
./scripts/ws-server
```

Start 2 consoles with different user ids and send messages:

```
python ./runners/ws-console.py --user-id user-1

python ./runners/ws-console.py --user-id user-2
```


### Kafka

The crypto example run an actor based server that reads from a kafka topic and uses a set of actors to process each message.

```
docker exec -it redpanda-1 rpk topic create crypto

python runners/crypto-server.py --app crypto

python runners/crypto-client.py --topic crypto
```

The chess example ...

```
python runners/chess-kafka-server.py --app chess

python runners/chess-kafka-client.py --topic chess --file ./data/chess/mega2400_part_01.pgn.txt
```

Publish kafka message:

```
python ./runners/py-cli topic-write  --topic test
```


### Zerorpc Example

The zerorpc examples uses rpc to implement a simple users service.

Start the server first (defaults to port 4242):

```
python ./runners/rpc-server.py
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
python ./runners/chess-zero-sink.py

python ./runners/chess-zero-filter.py

python runners/chess-zero-source.py
```

### Curio Channel

This example uses curio channels between a producer and consumer to send messages.

Start the producer first:

```
python ./runners/chess-curio-source.py
```

Then start the consumer:

```
python ./runners/chess-curio-sink.py
```
