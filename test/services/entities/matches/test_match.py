import pytest
import sqlmodel
import ulid

import models
import services.entities.matches
import services.entities.watches


@pytest.fixture()
def watch_ids(session: sqlmodel.Session):
    # create watch
    objects = [
        {
            "name": "watch-test",
            "query": "entity_name:person",
            "route": "queue:test",
        }
    ]

    struct_watches = services.entities.watches.Create(db=session, objects=objects).call()

    assert struct_watches.code == 0
    assert struct_watches.count == 1

    yield struct_watches.ids


def test_entity_match(session: sqlmodel.Session, watch_ids: list[int]):
    entity = models.Entity(
        entity_id=ulid.new().str,
        entity_name="person",
        slug="first_name",
        type_name="string",
        type_value="first",
    )

    struct_create = services.entities.matches.Create(db=session, entity=entity).call()

    assert struct_create.code == 0
    assert struct_create.count == 1

    struct_list = services.entities.matches.List(db=session, query="", offset=0, limit=100).call()

    assert struct_list.code == 0
    assert struct_list.count == 1

    entity_match = struct_list.objects[0]

    assert entity_match.entity_id == entity.entity_id


def test_entity_match__nomatch(session: sqlmodel.Session, watch_ids: list[int]):
    entity = models.Entity(
        entity_id=ulid.new().str,
        entity_name="case",
        slug="first_name",
        type_name="string",
        type_value="first",
    )

    struct_create = services.entities.matches.Create(db=session, entity=entity).call()

    assert struct_create.code == 0
    assert struct_create.count == 0
