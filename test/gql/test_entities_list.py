import test

import pytest
import sqlmodel
import strawberry
import strawberry.schema.config
import ulid

import gql
import services.entities
import services.graph
import services.users

gql_schema = strawberry.Schema(
    query=gql.Query,
    config=strawberry.schema.config.StrawberryConfig(auto_camel_case=False),
)


@pytest.fixture()
def entity_id(session: sqlmodel.Session):
    entity_id = ulid.new().str

    entity = test.EntityFactory.build(
        entity_id=entity_id,
    )

    struct_create = services.entities.Create(db=session, entities=[entity]).call()

    yield entity_id

    services.entities.delete_by_id(db=session, ids=struct_create.ids)  # type: ignore


def test_gql_entities_list(session: sqlmodel.Session, entity_id: str):
    query = """
        query TestQuery($query: String, $offset: Int, $limit: Int) {
            entities_list(query: $query, offset: $offset, limit: $limit) {
                code
                objects {
                    entity_id
                }
            }
        }
    """

    result = gql_schema.execute_sync(
        query,
        variable_values={"query": ""},
        context_value={"db": session},
    )

    assert result.errors is None

    data = result.data["entities_list"]

    assert data["code"] == 0
    assert len(data["objects"]) == 1
    assert data["objects"][0]["entity_id"] == entity_id
