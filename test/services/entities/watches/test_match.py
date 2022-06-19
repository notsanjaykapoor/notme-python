import pytest
import sqlmodel
import ulid

import services.entities.watches


class TestWatchTopic:
    @pytest.fixture()
    def entity_ids(self, session: sqlmodel.Session):
        objects = [
            {
                "entity_id": ulid.new().str,
                "entity_name": "any",
                "name": "person 1",
                "slug": "first_name",
                "type_name": "string",
                "type_value": "first",
            },
        ]

        struct_create = services.entities.Create(
            db=session,
            objects=objects,
        ).call()

        assert struct_create.code == 0

        yield struct_create.ids

    @pytest.fixture()
    def watch_ids(self, session: sqlmodel.Session):
        # create watch
        objects = [
            {
                "output": "anything",
                "query": "",
                "topic": "topic",
            }
        ]

        struct_watches = services.entities.watches.Create(db=session, objects=objects).call()

        assert struct_watches.code == 0
        assert struct_watches.count == 1

        yield struct_watches.ids

    def test_topic_match(self, session: sqlmodel.Session, watch_ids: list[int], entity_ids: list[int]):
        # with topic match
        struct_matches = services.entities.watches.Match(db=session, entity_ids=entity_ids, topic="topic").call()

        assert struct_matches.code == 0
        assert struct_matches.count == 1

        # with topic nomatch
        struct_matches = services.entities.watches.Match(db=session, entity_ids=entity_ids, topic="bogus").call()

        assert struct_matches.code == 0
        assert struct_matches.count == 0


class TestWatchQueryAll:
    @pytest.fixture()
    def entity_ids(self, session: sqlmodel.Session):
        objects = [
            {
                "entity_id": ulid.new().str,
                "entity_name": "any",
                "name": "person 1",
                "slug": "first_name",
                "type_name": "string",
                "type_value": "first",
            },
        ]

        struct_create = services.entities.Create(
            db=session,
            objects=objects,
        ).call()

        assert struct_create.code == 0

        yield struct_create.ids

    @pytest.fixture()
    def watch_ids(self, session: sqlmodel.Session):
        # create watch
        objects = [
            {
                "output": "anything",
                "query": "",
                "topic": "test",
            }
        ]

        struct_watches = services.entities.watches.Create(db=session, objects=objects).call()

        assert struct_watches.code == 0
        assert struct_watches.count == 1

        yield struct_watches.ids

    def test_entity_match(self, session: sqlmodel.Session, watch_ids: list[int], entity_ids: list[int]):
        struct_matches = services.entities.watches.Match(db=session, entity_ids=entity_ids).call()

        assert struct_matches.code == 0
        assert struct_matches.count == 1

        watch = struct_matches.watches[0]

        assert [watch.id] == watch_ids


class TestWatchQueryEntityName:
    @pytest.fixture()
    def entity_person_ids(self, session: sqlmodel.Session):
        objects = [
            {
                "entity_id": ulid.new().str,
                "entity_name": "person",
                "name": "person 1",
                "slug": "first_name",
                "type_name": "string",
                "type_value": "first",
            },
        ]

        struct_create = services.entities.Create(
            db=session,
            objects=objects,
        ).call()

        assert struct_create.code == 0

        yield struct_create.ids

    @pytest.fixture()
    def entity_case_ids(self, session: sqlmodel.Session):
        objects = [
            {
                "entity_id": ulid.new().str,
                "entity_name": "case",
                "name": "case 1",
                "slug": "jacket_id",
                "type_name": "string",
                "type_value": "1",
            },
        ]

        struct_create = services.entities.Create(
            db=session,
            objects=objects,
        ).call()

        assert struct_create.code == 0

        yield struct_create.ids

    @pytest.fixture()
    def watch_ids(self, session: sqlmodel.Session):
        # create watch
        objects = [
            {
                "output": "anything",
                "query": "entity_name:person",
                "topic": "test",
            }
        ]

        struct_watches = services.entities.watches.Create(db=session, objects=objects).call()

        assert struct_watches.code == 0
        assert struct_watches.count == 1

        yield struct_watches.ids

    def test_entity_match(self, session: sqlmodel.Session, watch_ids: list[int], entity_person_ids: list[int]):
        struct_matches = services.entities.watches.Match(db=session, entity_ids=entity_person_ids).call()

        assert struct_matches.code == 0
        assert struct_matches.count == 1

        watch = struct_matches.watches[0]

        assert [watch.id] == watch_ids

    def test_entity_nomatch(self, session: sqlmodel.Session, watch_ids: list[int], entity_case_ids: list[int]):
        struct_matches = services.entities.watches.Match(db=session, entity_ids=entity_case_ids).call()

        assert struct_matches.code == 0
        assert struct_matches.count == 0
