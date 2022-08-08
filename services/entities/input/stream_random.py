import random
import typing

import ulid


def stream_random(records: int) -> typing.Generator[tuple[int, dict], None, None]:
    entity_id = ulid.new().str

    if records < 500:
        buckets = 50
    elif records < 1000:
        buckets = int(records / 10)
    else:
        buckets = int(records / 100)

    object: dict = {
        "model": "person",
        "properties": [
            {"slug": "id", "type": "string", "value": ""},
            {"slug": "first_name", "type": "string", "value": "person"},
            {"slug": "last_name", "type": "string", "value": "0"},
            {"slug": "record_id", "type": "string", "value": ""},
            {"slug": "record_id", "type": "string", "value": ""},
        ],
        "id": "",
        "name": "person 4",
    }

    for i in range(0, records, 1):
        entity_id = ulid.new().str
        entity_name = f"person {i}"
        last_name = str(i)
        record_id_1 = str(random.randrange(buckets))

        record_id_2 = str(random.randrange(buckets))
        while record_id_2 == record_id_1:
            record_id_2 = str(random.randrange(buckets))

        object["id"] = entity_id
        object["name"] = entity_name
        object["properties"][0]["value"] = entity_id
        object["properties"][2]["value"] = last_name
        object["properties"][3]["value"] = record_id_1
        object["properties"][4]["value"] = record_id_2

        yield i, object
