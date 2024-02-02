import os
import re
import typing

import neo4j


def get(uri: typing.Optional[str] = None) -> neo4j.Session:
    return _get_driver(uri=uri).session(database=_get_db_name(uri=uri))


def _get_db_name(uri: typing.Optional[str] = None) -> str:
    """get neo4j database name"""
    if not uri:
        return os.environ["NEO4J_DB_NAME"]

    match = re.search(r"(.+)/([a-z0-9_]+)", uri)

    if not match:
        return os.environ["NEO4J_DB_NAME"]

    return match[2]


def _get_driver(uri: typing.Optional[str] = None) -> neo4j.Driver:
    if not uri:
        uri = os.environ["NEO4J_HOST_URL"]

    if match := re.search(r"^neo4j://(\S+):(\S+)@(.+):(.+)", uri):
        usr, pwd, host, port = match[1], match[2], match[3], match[4]
        uri_ = f"neo4j://{host}:{port}"
    elif match := re.search(r"^neo4j://(.+):(.+)", uri):
        usr = os.environ["NEO4J_USER"]
        pwd = os.environ["NEO4J_PASSWORD"]
        host, port = match[1], match[2]
        uri_ = f"neo4j://{host}:{port}"
    else:
        # hope the uri is valid
        uri_ = uri
        # raise ValueError("invalid uri")

    driver = neo4j.GraphDatabase.driver(uri_, auth=(usr, pwd))

    return driver
