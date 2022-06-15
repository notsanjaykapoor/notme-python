import pytest
import sqlmodel
import ulid

import models
import services.entities.watches


class TestWatchContext:
    @pytest.fixture()
    def watch_ids(self, session: sqlmodel.Session):
        # create watch
        objects = [
            {
                "output": "output",
                "query": "",
                "topic": "test",
            }
        ]

        struct_watches = services.entities.watches.Create(db=session, objects=objects).call()

        assert struct_watches.code == 0
        assert struct_watches.count == 1

        yield struct_watches.ids

    def test_context_match(self, session: sqlmodel.Session, watch_ids: list[int]):
        entity = models.Entity(
            entity_id=ulid.new().str,
            entity_name="any",
            slug="first_name",
            type_name="string",
            type_value="first",
        )

        # with context match
        struct_matches = services.entities.watches.Match(db=session, entity=entity, topic="test").call()

        assert struct_matches.code == 0
        assert struct_matches.count == 1

        # with context nomatch
        struct_matches = services.entities.watches.Match(db=session, entity=entity, topic="bogus").call()

        assert struct_matches.code == 0
        assert struct_matches.count == 0


class TestWatchQueryAll:
    @pytest.fixture()
    def watch_ids(self, session: sqlmodel.Session):
        # create watch
        objects = [
            {
                "output": "output",
                "query": "",
                "topic": "test",
            }
        ]

        struct_watches = services.entities.watches.Create(db=session, objects=objects).call()

        assert struct_watches.code == 0
        assert struct_watches.count == 1

        yield struct_watches.ids

    def test_entity_match(self, session: sqlmodel.Session, watch_ids: list[int]):
        entity = models.Entity(
            entity_id=ulid.new().str,
            entity_name="person",
            slug="first_name",
            type_name="string",
            type_value="first",
        )

        struct_matches = services.entities.watches.Match(db=session, entity=entity).call()

        assert struct_matches.code == 0
        assert struct_matches.count == 1

        watch = struct_matches.watches[0]

        assert [watch.id] == watch_ids


class TestWatchQueryEntityName:
    @pytest.fixture()
    def watch_ids(self, session: sqlmodel.Session):
        # create watch
        objects = [
            {
                "output": "test",
                "query": "entity_name:person",
                "topic": "test",
            }
        ]

        struct_watches = services.entities.watches.Create(db=session, objects=objects).call()

        assert struct_watches.code == 0
        assert struct_watches.count == 1

        yield struct_watches.ids

    def test_entity_match(self, session: sqlmodel.Session, watch_ids: list[int]):
        entity = models.Entity(
            entity_id=ulid.new().str,
            entity_name="person",
            slug="first_name",
            type_name="string",
            type_value="first",
        )

        struct_matches = services.entities.watches.Match(db=session, entity=entity).call()

        assert struct_matches.code == 0
        assert struct_matches.count == 1

        watch = struct_matches.watches[0]

        assert [watch.id] == watch_ids

    def test_entity_nomatch(self, session: sqlmodel.Session, watch_ids: list[int]):
        entity = models.Entity(
            entity_id=ulid.new().str,
            entity_name="case",
            slug="first_name",
            type_name="string",
            type_value="first",
        )

        struct_matches = services.entities.watches.Match(db=session, entity=entity).call()

        assert struct_matches.code == 0
        assert struct_matches.count == 0
