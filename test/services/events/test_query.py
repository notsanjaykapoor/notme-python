import pytest
import sqlmodel

import services.events


@pytest.mark.skip(reason="timescaledb support required")
def test_event_query(session: sqlmodel.Session):
    objects = [
        {
            "name": "entity.created",
            "value": 1.0,
        },
        {
            "name": "entity.created",
            "value": 1.0,
        },
        {
            "name": "entity.created",
            "value": 1.0,
        },
    ]

    for object in objects:
        struct_create = services.events.Create(db=session, object=object).call()
        assert struct_create.code == 0

    # timescale aggregate query
    results = session.execute(
        "select time_bucket('1 day', timestamp) as bucket, name, count(value) from events WHERE timestamp > now() - INTERVAL '1 week' group by bucket,name"
    )

    buckets = results.all()

    assert len(buckets) == 1
    assert buckets[0]["count"] == 3
    assert buckets[0]["name"] == "entity.created"

    services.events.truncate(db=session)
