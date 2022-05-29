from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import mgclient


class MemgraphConnection:
    def __init__(self):
        self._host = "127.0.0.1"
        self._port = 7687
        self._connection = mgclient.connect(host=self._host, port=self._port)

    def commit(self):
        self._connection.commit()

    def connection(self):
        return self._connection

    def cursor(self):
        return self._connection.cursor()

    def query_count_nodes(self):
        return "MATCH (n) RETURN count(n)"

    def query_delete_all(self):
        return "MATCH (n) DETACH DELETE n"

    def query_match_all(self):
        return "MATCH (n) RETURN n"
