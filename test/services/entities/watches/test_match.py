import test

import neo4j
import pytest
import sqlmodel
import ulid

import services.entities
import services.entity_watches


class TestWatchTopic:
    @pytest.fixture()
    def entity_ids(self, session: sqlmodel.Session):
        entity = test.EntityFactory.build(
            entity_id=ulid.new().str,
        )

        struct_create = services.entities.Create(db=session, entities=[entity]).call()

        assert struct_create.code == 0

        yield struct_create.ids

        services.entities.delete_by_id(db=session, ids=struct_create.ids)  # type: ignore

    @pytest.fixture()
    def watch_ids(self, session: sqlmodel.Session):
        # create watch
        objects = [
            {
                "message": "any",
                "output": "any",
                "query": "",
                "topic": "topic",
            }
        ]

        struct_watches = services.entity_watches.Create(db=session, objects=objects).call()

        assert struct_watches.code == 0
        assert struct_watches.count == 1

        yield struct_watches.ids

        services.entity_watches.delete_by_id(db=session, ids=struct_watches.ids)

    def test_topic_match(self, session: sqlmodel.Session, neo_session: neo4j.Session, watch_ids: list[int], entity_ids: list[int]):
        # with topic match
        struct_matches = services.entity_watches.Match(db=session, neo=neo_session, entity_ids=entity_ids, topic="topic").call()

        assert struct_matches.code == 0
        assert struct_matches.count == 1

        # with topic nomatch
        struct_matches = services.entity_watches.Match(db=session, neo=neo_session, entity_ids=entity_ids, topic="bogus").call()

        assert struct_matches.code == 0
        assert struct_matches.count == 0


class TestWatchQueryAll:
    @pytest.fixture()
    def entity_ids(self, session: sqlmodel.Session):
        entity = test.EntityFactory.build(
            entity_id=ulid.new().str,
        )

        struct_create = services.entities.Create(db=session, entities=[entity]).call()

        assert struct_create.code == 0

        yield struct_create.ids

        services.entities.delete_by_id(db=session, ids=struct_create.ids)  # type: ignore

    @pytest.fixture()
    def watch_ids(self, session: sqlmodel.Session):
        # create watch
        objects = [
            {
                "message": "any",
                "output": "any",
                "query": "",
                "topic": "test",
            }
        ]

        struct_watches = services.entity_watches.Create(db=session, objects=objects).call()

        assert struct_watches.code == 0
        assert struct_watches.count == 1

        yield struct_watches.ids

        services.entity_watches.delete_by_id(db=session, ids=struct_watches.ids)

    def test_entity_match(self, session: sqlmodel.Session, neo_session: neo4j.Session, watch_ids: list[int], entity_ids: list[int]):
        struct_matches = services.entity_watches.Match(db=session, neo=neo_session, entity_ids=entity_ids).call()

        assert struct_matches.code == 0
        assert struct_matches.count == 1

        watch = struct_matches.watches[0]

        assert [watch.id] == watch_ids


class TestWatchQueryEntityName:
    @pytest.fixture()
    def entity_person_ids(self, session: sqlmodel.Session):
        entity = test.EntityFactory.build(
            entity_id=ulid.new().str,
            entity_name="person",
        )

        struct_create = services.entities.Create(db=session, entities=[entity]).call()

        assert struct_create.code == 0

        yield struct_create.ids

        services.entities.delete_by_id(db=session, ids=struct_create.ids)  # type: ignore

    @pytest.fixture()
    def entity_case_ids(self, session: sqlmodel.Session):
        entity_id = ulid.new().str

        entity = test.EntityFactory.build(
            entity_id=entity_id,
            entity_name="case",
            name="case 1",
            slug="jacket_id",
            type_name="string",
            type_value="1",
        )

        struct_create = services.entities.Create(
            db=session,
            entities=[entity],
        ).call()

        assert struct_create.code == 0
        assert struct_create.count == 1

        yield struct_create.ids

        services.entities.delete_by_id(db=session, ids=struct_create.ids)  # type: ignore

    @pytest.fixture()
    def watch_ids(self, session: sqlmodel.Session, neo_session: neo4j.Session):
        # create watch
        objects = [
            {
                "message": "any",
                "output": "any",
                "query": "entity_name:person",
                "topic": "test",
            }
        ]

        struct_watches = services.entity_watches.Create(db=session, objects=objects).call()

        assert struct_watches.code == 0
        assert struct_watches.count == 1

        yield struct_watches.ids

        services.entity_watches.delete_by_id(db=session, ids=struct_watches.ids)

    def test_entity_match(self, session: sqlmodel.Session, neo_session: neo4j.Session, watch_ids: list[int], entity_person_ids: list[int]):
        struct_matches = services.entity_watches.Match(db=session, neo=neo_session, entity_ids=entity_person_ids).call()

        assert struct_matches.code == 0
        assert struct_matches.count == 1

        watch = struct_matches.watches[0]

        assert [watch.id] == watch_ids

    def test_entity_nomatch(self, session: sqlmodel.Session, neo_session: neo4j.Session, watch_ids: list[int], entity_case_ids: list[int]):
        struct_matches = services.entity_watches.Match(db=session, neo=neo_session, entity_ids=entity_case_ids).call()

        assert struct_matches.code == 0
        assert struct_matches.count == 0


class TestWatchQueryGeoFence:
    @pytest.fixture()
    def entity_place_ids(self, session: sqlmodel.Session):
        entity = test.EntityFactory.build(
            entity_id=ulid.new().str,
        )

        struct_create = services.entities.Create(db=session, entities=[entity]).call()

        assert struct_create.code == 0

        yield struct_create.ids

    @pytest.fixture()
    def watch_ids(self, session: sqlmodel.Session):
        # create watch
        objects = [
            {
                "message": "any",
                "output": "any",
                "query": "entity_name:place geofence:41.8911752,-87.6321491,2mi",
                "topic": "test",
            }
        ]

        struct_watches = services.entity_watches.Create(db=session, objects=objects).call()

        assert struct_watches.code == 0
        assert struct_watches.count == 1

        yield struct_watches.ids

        services.entity_watches.delete_by_id(db=session, ids=struct_watches.ids)

    def test_entity_match(self, session: sqlmodel.Session, neo_session: neo4j.Session, watch_ids: list[int], entity_place_ids: list[int], mocker):
        service = services.entity_watches.Match(db=session, neo=neo_session, entity_ids=entity_place_ids)

        m = mocker.patch.object(service, "_watch_entity_geo_query", return_value=["record"])

        struct_matches = service.call()

        m.assert_called_once()

        assert struct_matches.code == 0
        assert struct_matches.count == 1

        watch = struct_matches.watches[0]

        assert [watch.id] == watch_ids
