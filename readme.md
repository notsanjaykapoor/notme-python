### Setup

Start server:

```
uvicorn main:app --reload
```

### Curl

List users:

```
curl http://127.0.0.1:8000/users
```

### Cli

List users:

```
python3 cli.py user-search
```

Create user:

```
python3 cli.py  user-create user-1
```


Publish message:

```
python3 cli.py topic-publish test
```
